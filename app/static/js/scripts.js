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
		$('.Status').html("<span><div class=\"status-light-profile sl-red pull-left\"></div><div class=\"pull-left\">OFFLINE</div></span>")
        }
        else {
    		$('.Status').html("<span><div class=\"status-light-profile sl-green pull-left\"></div><div class=\"pull-left\">LIVE</div></span>")
        }
 }
});
}

function selectRandomBackground() {
$(document).ready(function() {

  var random= Math.floor(Math.random() * 5) + 0;
  var wallpapers = ["url('/static/img/pubg.jpg')", "url('/static/img/fh4.jpg')", "url('/static/img/fortnite.jpg')", "url('/static/img/halo.jpg')", "url('/static/img/nfs.jpg')"];
  document.body.style.backgroundImage=wallpapers[random]; //content
});

}
