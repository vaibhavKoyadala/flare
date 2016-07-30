App={
    models:{},
    collections:{},
    views:{},
    routers: {}
}
instance={
    models:{},
    collections:{},
    views:{},
    routers: {}
}


//  MODELS
App.models.TextMessage = Backbone.Model.extend({
    url: 'api/send',
    defaults: function(){
        return {timestamp: new Date($.now())}
    },
    send: function(){
        that = this
        console.log(that.get('text'))
        $.post( that.url, {text: that.get('text')},
                function(data, status){
                    console.log(data)
                    that.set('uploaded', true)
                })
    },
	parse: function(response, options){
		response['timestamp'] = new Date(response['timestamp'])
		return response
	}
})
App.models.FileMessage = Backbone.Model.extend({
    bytesToString: function(bytes){
		prefix = 'Bytes'
		if(bytes >= 1024){
			bytes = bytes/1024
			prefix = 'KB'
		}
		if(bytes >= 1024){
			bytes = bytes/1024
			prefix = 'MB'
		}
		if(bytes >= 1024){
			bytes = bytes/1024
			prefix = 'GB'
		}
		return bytes.toFixed(2).toString() + ' ' + prefix
	},
	parse: function(response, options){
		response['timestamp'] = new Date(response['timestamp'])
		return response
	}
})
App.models.Joker = Backbone.Model.extend({
    fetch: function(){
        that = this
        $.ajax('api/account', {
			success: function(data){
				_.extend(that, data)
			},
			error: function(){
				showStatus('Failed to set-up account. Hhmmm.')
			},
			async: false
		});
    }
})
//  COLLECTIONS
App.collections.TextMessages = Backbone.Collection.extend({
    url: 'api/messages',
    ajaxObj: null,
    fetch: function(){
		console.log('checking  if null')
        // Return if a request is already running
        if(this.ajaxObj != null)return
        
        url = this.url
        data = {}
        if(this.length){
            data['fetch_from'] = this.at(-1).get('timestamp').toISOString()
			console.log('fetching from '+data['fetch_from'])
        }
		that = this
		this.ajaxObj = $.ajax({
			url, 
			data, 
			success: function(data, status){
				console.log(data)
				that.ajaxObj = null
				_.forEach(data, function(obj){
					this.add(new App.models.TextMessage(obj, {parse: true}))
				}, that)

			},
			error: function(){
				that.ajaxObj = null
				showToast("Looks I can't fetch your messages.", 'warn')
			},
			complete: function(){
				console.log('completed')
				
			}})
			console.log('Fetch ajax sent')
        
    }
})
App.collections.FileMessages = Backbone.Collection.extend({
    url: 'api/files',
    ajaxObj: null,
    fetch: function(){
        // Return if a request is already running
        if(this.ajaxObj != null) return
        
        url = this.url
        url = this.url
        data = {}
		console.log(this.at(-1))
        if(this.length){
            data['fetch_from'] = this.at(-1).get('timestamp').toISOString()
        }
		console.log(data['fetch_from'])
		that = this
		
		this.ajaxObj = $.ajax({
			url, 
			data, 
			success: function(data, status){	
					_.forEach(data, function(obj){
							console.log(obj)
							that.add(new App.models.FileMessage(obj, {parse: true}))
						}, that)
						console.log('Length '+that.size())
						that.ajaxObj = null
			},
			error: function(){
				showStatus("Okay, the files couldn't be loaded. Wierd.", 'warn')
				that.ajaxObj = null
			}
		})
		console.log('Length '+this.size())
	}
	
})
//  MODEL VIEWS 
App.views.TextMessage = Backbone.View.extend({
    template:{
        message: _.template("<p class='joker'><%=joker_name%></p>"+
                            "<p class='text'><%=text%></p>"),
        selfMessage: _.template("<p class='text'><%=text%></p>"),
        infoMessage: _.template("<p><%=text%></p>")
    },
    render: function(){
        model = this.model
		text = model.get('text')
        joker_name = model.get('joker_name')
        if(text.charAt(0) == ':' && text.charAt(-1) == ':'){
            template = this.template.infoMessage
            text = "".slice(1, -1)
			this.className = 'message-info'
        }else if(joker_name == 'self'){
            template = this.template.selfMessage
			this.className = 'message-self'
		}else{
            template = this.template.message
			this.className = 'message'
		}this.$el.html(template({text, joker_name}))
		this.$el.attr('class', this.className)
		return this.$el
    }
    
})
App.views.FileMessage = Backbone.View.extend({
    thumbnailTemplate: _.template(	'<div class="center">'+
									'<img src="<%=thumbnail_url%>" >'+
									'</div>'+
									'<div class="file-size"><%=size%></div>'),
    titleTemplate: _.template(	'<span><%=title%></span>'+
								'<div class="file-size"><%=size%></div>'),
	className: 'file-msg',
	
	events: {
		'click': 'click',
		'mouseover': 'hover'
	},
    render: function(){
        model = this.model
		if(model.get('thumbnail_url'))
			template = this.thumbnailTemplate
		else
			template = this.titleTemplate
		data = model.attributes
		console.log(data)
		data['size'] = model.bytesToString(data['size'])
		
		this.$el.html(template(data))
		return this.$el
	},
	'click': function(){
		window.location.href = this.model.get('url')
	},
	'hover': function(){
		
	}
})
// VIEW TEXT MESSAGE
App.views.TextMessages = Backbone.View.extend({
    initialize: function(){
		this.collection.on('add', this.append, this)
		this.$el.html()
	},
	append: function(model){
		console.log('Appending')
		this.$el.append(new App.views.TextMessage({model}).render())
	}
})
 // VIEW FILE MESSAGE
App.views.FileMessages = Backbone.View.extend({
    initialize: function(){
        this.collection.on('add', this.append, this)
        this.$el.html()
    },
    append: function(model){
        console.log('Appending')
		this.$el.append(new App.views.FileMessage({model}).render())
    }
})
App.routers.Router = Backbone.Router.extend({
    routes:{
        '': 'text-messages',
        'text-messages': 'text-messages',
        'file-messages': 'file-messages',
        'account': 'account',
    },
    'text-messages': function(){
        console.log('router :: text-messages')
        this.showTextMessages()
    },
    'file-messages': function(){
        console.log('router :: file-messages')
        this.showFileMessages()
    },
    'account': function(){
        console.log('router :: account')
        this.showAccount()
    },
    // Text messages
    showTextMessages: function(){
        this.hideFileMessages()
        this.hideAccount()
        $('#text-messages-content').show()
        $('#text-messages-footer').show()
    },
    hideTextMessages: function(){
        $('#text-messages-content').hide()
        $('#text-messages-footer').hide()
    },
    
    // File messages
    showFileMessages: function(){
		fetchFileMessages()
        this.hideTextMessages()
        this.hideAccount()
        $('#file-messages-content').show()
        $('#file-messages-footer').show()
        $('#file-messages-button').html('<a href="#text-messages"> &ltBack </a>')
    },
    hideFileMessages: function(){
        $('#file-messages-content').hide()
        $('#file-messages-footer').hide()
        $('#file-messages-button').html('<a href="#file-messages"> FILES </a>')
    },
    
    // Account
    showAccount: function(){
        this.hideTextMessages()
        this.hideFileMessages()
        $('#account-content').show()
        $('#account-button').html('<a href="#text-messages"> &ltBack </a>')
    },
    hideAccount: function(){
        $('#account-content').hide()
        $('#account-button').html('<a href="#account"> flare_name </a>'.replace("flare_name", instance.joker.flare.name))
        
    },
    
})
function fetchTextMessages(){
	console.log('Trying to fetch text messages')
	instance.collections.TextMessages.fetch()
} 
function fetchFileMessages(){
	console.log('Trying to fetch file messages')
	instance.collections.FileMessages.fetch()
}
function sendTextMessage(e){
    // Take the text from the input box, send it
    text = $('#text-message-input').val()
    if(text == "") return;
    console.log('sending '+text)
    data = {text}
    $.ajax({
		url: 'api/send', 
		data, 
		success: function(data, status){
			$('#text-message-input').val('')
			fetchTextMessages()
		},
		error: function(){
			showToast('Drat, your message got lost !', 'warn')
		},
		method: 'POST'
	})
		
}
function sendFileMessage(e){
    // Take the text from the input box, send it
    
	var submitButton = $('#file-message-submit')
	submitButton.hide()
	console.log('Trying to send file message')
	
	$.ajax({
		url: 'api/upload',
		type: 'post',
		data: new FormData($('#file-message-form')[0]),
		processData: false,
		cache: false,
		contentType: false,
		success: function(){
			showToast("File sent!", 'success')
			fetchFileMessages()
		},
		error: function(){
			showToast("Your file could'nt be upload", 'warn')
		}
	});
	e.preventDefault()
}
function showToast(message, type){
	var background, color
	if(type=='success'){
		background = 'rgba(193, 35, 64, 0.9)'
		color = 'white'
	}else 
	if(type=='warn'){
		background = 'rgba(91, 200, 219, 0.9)'
		color = 'white'
	}else{
		background = 'rgb(148, 77, 81)';
		color = 'white';
	}
	statusBar = $('#status-bar')
	statusBar.html(message)
	statusBar.css({'background': background})
	statusBar.css({'color': color})
	statusBar.slideDown()
	setTimeout(function(){ statusBar.slideUp() }, 5000)
}


function init_file_form(){
    $('#file-msg-form').ajaxForm()
}
$(document).ready(function(){
    instance.joker = new App.models.Joker()
    instance.joker.fetch()
    instance.collections.TextMessages = new App.collections.TextMessages()
    instance.collections.FileMessages = new App.collections.FileMessages()
    instance.views.TextMessages = new App.views.TextMessages({el: '#text-messages-content', collection: instance.collections.TextMessages})
    instance.views.TextMessages = new App.views.FileMessages({el: '#file-messages-content', collection: instance.collections.FileMessages})
    instance.routers.Router = new App.routers.Router()
    Backbone.history.start();
    
    
    // Fetch file messages every 5 seconds
    setInterval(fetchTextMessages, 5000)
    
	// Set up listeners
    $('#text-message-input').keydown(function(e){
		if(e.which == 13)
			sendTextMessage()
	})
	$('#text-message-submit').click(sendTextMessage)
	
	$('#file-message-form').submit(sendFileMessage)
	
	console.log($('').qrcode)
	$('#qrcode').qrcode({
		/*A hack: Use the element holding the flare's name to get the flare name*/
		/*TODO: This ain't right. Add support in the API to get the current session's details.*/
		
		text: 'http://' + $(location).attr('hostname') + '/join?flare="{}"'.replace('{}', $('#flarename').text())
	})
	showToast('', '')
	console.log('Setup done !')
	
	
})

