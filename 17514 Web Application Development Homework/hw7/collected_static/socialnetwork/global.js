"use strict"

/**
 * Send XMLHttpRequest(GET) to socialnetwork/get-global.
 * xhr.responseText expect to be json-like string that send by 
 * <get_post_json_dumps_serializer> from views.py
 * After that, run updatePost(xhr) to update pages
 */
function getPost() {    
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePost(xhr)
    }

    xhr.open("GET", "/socialnetwork/get-global", true)
    xhr.send()
}

/**
 * If xhr is valid, run updatePostHelper to update global posts and comments 
 * @param {*} xhr XMLHttpRequest that contains up-to-date data
 * @returns 
 */
function updatePost(xhr) {
    if (xhr.status == 200) {    
        let response = JSON.parse(xhr.responseText)
        updatePostHelper(response)
        return
    }

    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }


    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

/**
 * updatePost pass the json object data that contains up-to-date 
 * posts and comments data
 * In updatePostHelper, check all data and see whether current html has render the element
 * if not, create and filled the attributes, else, kindly ignore it because no update needed
 * @param {*} data 
 */
function updatePostHelper(data) {
    let posts = data["posts"]
    let comments = data["comments"]    
    // before update the post, need to clear all previous posts
    let container = document.getElementById("post-container")  
    
    // Adds each new post item to the list
    for (let i = 0; i < posts.length; i++) {           
        let post = posts[i]
        if (document.getElementById("id_post_and_comment_div_"+ post['id']) == null) {                    
            // div that contain 1 post and many comments
            let post_and_comment_div = document.createElement("div")
            
            setAttributes(post_and_comment_div, {
                'id':'id_post_and_comment_div_' + post['id']
            });

            // create post html
            let post_div = document.createElement("div")
            setAttributes(post_div, {
                "class": "post",
                "id": "id_post_div_" + post["id"],
            });
            
            let post_date_time = document.createElement("p")
            setAttributes(post_date_time, {
                "class": "post_date_time",
                "id": "id_post_date_time_" + post['id']
            })                   
            post_date_time.innerHTML = post['creation_time']

            
            let post_profile = document.createElement("a");
            
            setAttributes(post_profile, {
                "class": "post_profile",
                "id": "id_post_profile_" + post['id'],
                "style": "None",
                "href": "other/" + post.user.id,
            });            
            post_profile.innerHTML = "Post by " + post.user.first_name + " " + post.user.last_name + " "
            
            let post_text = document.createElement("span")
            setAttributes(post_text, {
                "class": "post_text",
                "id": "id_post_text_" + post['id']
            })            
            post_text.innerHTML = sanitize(post['text'])
            
            let p = document.createElement("p").append(post_profile, post_text)            
            // post_div.append(p, post_date_time)
            post_div.append(post_profile, post_text, post_date_time)
            
            
            // create empty comment area 
            let comment_area = document.createElement("div");
            setAttributes(comment_area, {"id": "id_comment_area_" + post.id})
           
            let label = document.createElement("label")
            label.innerHTML = "Comment"

            let comment_input_text = document.createElement("input")
            
            setAttributes(comment_input_text, {
                "class": "comment_input_text",
                "id": "id_comment_input_text_" + post.id,
                "type": "text"
            })

            let submit_input = document.createElement("input")            
            setAttributes(submit_input, {
                "id": "id_comment_button_" + post.id,
                "type": "submit",
                "onclick": "addComment(" + post.id + ")"
            })
            
            comment_area.append(document.createElement("br"), label, comment_input_text, submit_input)        
            post_and_comment_div.append(post_div, comment_area)             
            container.prepend(post_and_comment_div)
        } 
    }
    
    
    for (let i = 0; i < comments.length; i++) {        
        let comment = comments[i];        
        if (document.getElementById("id_comment_div_" + comment.id) == null) {
            let comment_area = document.getElementById("id_comment_area_" + comment.post_id)            
            let comment_div = document.createElement("div")
            setAttributes(comment_div, {
                "class": "comment_div",
                "id": "id_comment_div_" + comment.id
            });
            
            let comment_profile = document.createElement("a")
            setAttributes(comment_profile, {
                "class": "comment_profile",
                "id": "id_comment_profile_" + comment.id,
                "href": "other/" + comment.user.id
            });            
            comment_profile.innerHTML =  comment.user.first_name + " " + comment.user.last_name + " : "
                    
            
            let comment_text = document.createElement("span")
            setAttributes(comment_text, {
                "class": "comment_text",
                "id": "id_comment_text_" + comment.id
            });            
            comment_text.innerHTML = comment.text
            
            let comment_date_time = document.createElement("span")
            setAttributes(comment_date_time, {
                "class": "comment_date_time",
                "id": "id_comment_date_time_" + comment.id
            });            
            comment_date_time.innerHTML = comment.creation_time;
            comment_div.append(comment_profile, comment_text, document.createElement("br"), 
                            comment_date_time)                       
            comment_area.append(comment_div, document.createElement("br"))            
        }
    }
}

/**
 * extract error span from global.html and add error message to it
 * @param {*} message 
 */
function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

/**
 * Sanitize post['text'], or else when setting element.innterhtml, 
 * something may not display as expected.
 * @param {*} s 
 * @returns string that was sanitized
 */
function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}


/**
 * Extract post data and send POST request to home with required data
 */
function addPost() {
    let itemTextElement = document.getElementById("id_post_input_text")
    let itemTextValue   = itemTextElement.value

    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePost(xhr)
    }

    xhr.open("POST", 'home', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded"); // not sure what this is 
    xhr.send("post_text="+itemTextValue+"&csrfmiddlewaretoken="+getCSRFToken());
}

/**
 * Extract comment data and send POST request to add-comment with required data
 * @param {*} id post id to identify comment div
 */
function addComment(id) {
    let comment_id  = "id_comment_input_text_" + id    
    let itemTextElement = document.getElementById(comment_id)
    let itemTextValue   = itemTextElement.value
    
    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return
        updatePost(xhr)
    }

    xhr.open("POST", 'add-comment', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("comment_text="+itemTextValue+"&post_id="+id+"&csrfmiddlewaretoken="+getCSRFToken());
}



/**
 * Extract getCSRFToken from document.cookie to pass the token when making POST request
 * because django views.py needs to ensure the source is valid 
 * @returns 
 */
function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

/**
 * Helper function to set multiple attributes of a html element concisely
 * @param {*} el the html element 
 * @param {*} options json object contain attributes and corresponding data
 */
function setAttributes(el, options) {
    Object.keys(options).forEach(function(attr) {
      el.setAttribute(attr, options[attr]);
    })
 }
 