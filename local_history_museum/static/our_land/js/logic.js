window.initializeCarousel=()=>{
    $('#carousel_img').carousel({
        interval: 500
    });
}


function addComment(name, id){
    $('#contactparent').val(id);
    $('#contactcomment').html(name + ', ');
}


// Загрузка комментариев 1 уровня
function LoadComments(elemCommentAnswer, elemMoreComments){
    let last_comment = $('.last-comment');
    let lastCommId = last_comment.attr('data-commentId');
    let artUrl = last_comment.attr('data-articleUrl');
    let data = {
        lastCommId: lastCommId,
        artUrl: artUrl,
    };

    let comment = $('.comments');
    comment.removeClass('last-comment');
    comment.removeAttr('data-commentId');
    comment.removeAttr('data-articleUrl');

    $.ajax({
        method: 'GET',
        dataType: 'json',
        data: data,
        url: '/ru/our_land/load-comments/',
        success: function (data){
            let result = data['data'];

            if (!result){
                $('#load-comments').css('display', 'none');
            } else {
                let liElement;

                $.each(result, function (key, obj){
                    if (obj['last-comment']){
                        liElement =
                            '<li class="media comments last-comment" ' +
                                'data-commentId="' + obj['id'] + '" ' +
                                'data-articleUrl="'+ artUrl + '">'
                    } else{
                        liElement = '<li class="media comments">'
                    }

                    liElement += renderComment(obj, true, elemCommentAnswer, elemMoreComments) + '</li>';
                    $('.all-comments').append(liElement)
                });
            }
        }
    });
}


// Загрузка комментариев 2 уровня
function LoadChildComments(parent, elemCommentAnswer, elemMoreComments){
    let last_comment = $('.' + parent);
    let lastChildCommId = last_comment.attr('data-childCommentId');
    let data = {
        lastChildCommId: lastChildCommId,
    };

    last_comment.removeClass('last-child-comment');
    last_comment.removeClass(parent.toString());
    last_comment.removeAttr('data-childCommentId');

    $.ajax({
        method: 'GET',
        dataType: 'json',
        data: data,
        url: '/ru/our_land/load-child-comments/',
        success: function (data){
            let result = data['data'];
            if (!result){
                $('#' + parent.toString() + 'btn').css('display', 'none');
            } else{
                let liElement;
                $.each(result, function (key, obj){
                    if(obj['last-comment']){
                        liElement =
                            '<li class="media child-comments last-child-comment ' + parent + '" ' +
                                'data-childCommentId="' + obj['id'] + '">';

                    } else {
                        liElement = '<li class="media child-comments">';
                    }
                    liElement += renderComment(obj, false, elemCommentAnswer, elemMoreComments) + '</li>';
                    $('#' + obj['parent']).append(liElement)
                })
            }
        }
    });
}


function renderChildComments(children, elemCommentAnswer, elemMoreComments){
    let length = children.length;
    let parent = 0;
    let result;

    if (length > 0){
        result = '<ul id="' + children[0]['parent'] + '" class="media-list">';
    } else{
        result = '<ul class="media-list">';
    }

    $.each(children, function(key, obj){
        parent = obj['parent'];
        if(key + 1 === length){
            result += '<li class="media child-comments last-child-comment ' + parent + '" data-childCommentId="' + obj['id'] + '">'
        } else{
            result += '<li class="media child-comments">'
        }
        result += renderComment(obj, false, elemCommentAnswer, elemMoreComments) + '</li>';
    });
    result += '</ul>'
    result +=
        '<ul class="mt-2"><li><a id="' + parent + 'btn" onclick="LoadChildComments(' + parent + ', \'' + elemCommentAnswer + '\', \'' + elemMoreComments + '\')" class="mt-3 load-comments-ref">' +
            elemMoreComments +
        '</a></li></ul>'

    return result
}


// Отрисовка комментария
function renderComment(obj, isParent, elemCommentAnswer, elemMoreComments){
    result =
        '<div class="media-body">' +
            '<div class="mb-0 media-heading">' +
                '<div class="author">' +
                    obj['name'] +
                '</div>' +
                '<div class="metadata">' +
                    '<span class="mt-0 email">' + obj['datetime']  + '</span>' +
                '</div>' +
            '</div>' +
            '<div class="media-text text-justify">' +
                obj['text'] +
            '</div>' +
            '<div class="footer-comment">' +
                '<span class="comment-reply">';
                if(isParent){
                    result +=
                        '<a href="#formComment" ' +
                            'onClick=\"addComment(\'' + obj['name'] + '\', \'' + obj['id'] +'\')\" ' +
                            'class="reply">' + elemCommentAnswer + '</a>';
                } else {
                    result +=
                        '<a href="#formComment" ' +
                            'onClick=\"addComment(\'' + obj['name'] + '\', \'' + obj['parent'] +'\')\" ' +
                            'class="reply">' + elemCommentAnswer + '</a>';
                }
                result += '</span>' + '</div>';
            if (isParent){
                result += renderChildComments(obj['children'], elemCommentAnswer, elemMoreComments);
            }
            result += '</div>';

    return result;
}


// Отправка комментария
function sendComment(articleId){
    data = {
        'parent': $('input:hidden[name=parent]').val(),
        'art': articleId,
        'name': $('input:text[name=name]').val(),
        'text': $('textarea[name=text]').val(),
        'g-recaptcha-response': $('input:hidden[name=g-recaptcha-response]').val(),
    }

    $.ajax({
        method: 'POST',
        dataType: 'json',
        data: data,
        url: '/ru/our_land/comments/',
        success: function (data){
            let modalGood = $('#modalGood');
            let modalBad = $('#modalBad');
            if(data['message']){
                modalGood.css('display', 'block');
            } else {
                modalBad.css('display', 'block');
            }
            setTimeout(function (){
                modalGood.css('display', 'none');
                modalBad.css('display', 'none');
            }, 2000);
        }
    });
}


function fadeMessage(){
    let modalGood = $('#modalGood');
    let modalBad = $('#modalBad');
    modalGood.css('display', 'none');
    modalBad.css('display', 'none');
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        var csrftoken = getCookie('csrftoken');
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function () {
    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
});