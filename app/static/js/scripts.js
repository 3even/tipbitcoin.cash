function GetURL(username) {
  $.ajax({
    type: 'GET',
    url: 'https://api.twitch.tv/helix/users?login='+username,
    headers: {
    'Client-ID': '7huj5qkr57zrkcak291aed6s941jjq'
  },
 success: function(data) {
   $(".ProfilePicture").attr('src', data.data[0].profile_image_url);
 }
});
}
function GetStreamStatus(username) {
  $.ajax({
 type: 'GET',
 url: 'https://api.twitch.tv/helix/streams?user_login='+username,
 headers: {
   'Client-ID': '7huj5qkr57zrkcak291aed6s941jjq'
 },
 success: function(data) {
        if(data.data.length == 0){
		$('.Status').html("<span><div class=\"status-light sl-red pull-left\"></div><div class=\"pull-left\">OFFLINE</div></span>")
        }
        else {
    		$('.Status').html("<span><div class=\"status-light sl-green pull-left\"></div><div class=\"pull-left\">LIVE</div></span>")
        }
 }
});
}
