function getLatestTweets() {
	$.get('http://localhost:5000/recent', function(data) {
		// clear div
		$(".recentTweets").empty()

		// append tweets
		for (var i = 0; i < data.length; i++) {
			$(".recentTweets").append("<p><b>Time</b>: " + data[i].time + "<br><b>Tweet</b>: " + data[i].tweet + "</p>")
		};
	});
}

function getFriendsWhoDontFolllow() {
	$.get('http://localhost:5000/friends', function(data) {
		// clear div
		$(".friendsNotFollow").empty()

		// append users
		for (var i = 0; i < data.length; i++) {
			$(".friendsNotFollow").append("<br>" + data[i] + "</br>");
		};
	});
}

function setup() {
	var getTweetsButton = document.getElementById('getTweetsButton');
	var getFriendsButton = document.getElementById('getFriendsButton');
	
	getTweetsButton.onclick = getLatestTweets;
	getFriendsButton.onclick = getFriendsWhoDontFolllow;
}

setup();