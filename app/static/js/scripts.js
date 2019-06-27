function GetURL(username) {
  $.ajax({
 type: 'GET',
 url: 'https://api.twitch.tv/kraken/channels/'+username,
 headers: {
    'Client-ID': 'n7j8ddl0pu87ig063e6mnr33on17xw'
 },
 success: function(data) {

   $(".ProfilePicture").attr('src', data.logo);
   $("#channel_info").html("<div>Followers: "+ data.followers +"</div>" +
                            "<div>Total Views: " + data.views + "<div>");

   // $("#ProfileBanner").attr('src', data.profile_banner);
 }
});
}

function GetBannerURL(username) {
  $.ajax({
    type: 'GET',
    url: 'https://api.twitch.tv/kraken/channels/'+username,
    headers: {
    'Client-ID': 'n7j8ddl0pu87ig063e6mnr33on17xw'
  },
  success: function(data) {
    if (data.profile_banner == null) {
      $("#ProfileBanner").css("height", "0");

    }
    else
      $("#ProfileBanner").css({"background" : "url('" + data.profile_banner + "') left bottom", "height" : "380px"});
    }
  });
}
function GetStreamStatus(username) {
  $.ajax({
 type: 'GET',
 url: 'https://api.twitch.tv/kraken/streams/'+username,
 headers: {
   'Client-ID': 'n7j8ddl0pu87ig063e6mnr33on17xw'
 },
 success: function(data) {
   if (data.stream == null) {
     $('.Status').html("<span><div class=\"status-light sl-red pull-left\"></div><div class=\"pull-left\">OFFLINE</div></span>")
   }
   else
    $('.Status').html("<span><div class=\"status-light sl-green pull-left\"></div><div class=\"pull-left\">LIVE</div></span>")
 }
});
}

function GetStreamStatusForUsers(username) {
  $.ajax({
 type: 'GET',
 url: 'https://api.twitch.tv/kraken/streams/'+username,
 headers: {
   'Client-ID': 'n7j8ddl0pu87ig063e6mnr33on17xw'
 },
 success: function(data) {
   if (data.stream == null) {
     $('.Status'+username).html("<div class=\"status-light sl-red pull-left\"></div>")
   }
   else
    $('.Status'+username).html("<div class=\"status-light sl-green pull-left\"></div>")
 }
});
}
