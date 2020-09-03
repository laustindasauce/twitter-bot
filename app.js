const axios = require('axios')

const tweets_liked_span = document.getElementById("tweets-liked")
const tweets_span = document.getElementById("tweets")
const followers_span = document.getElementById("followers")
const tweets_read_span = document.getElementById("tweets-read")

const BASE_URL = 'https://guldentech.com'

const getTwitterData = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/austinapi/tendie-intern`);

        followers_span.innerHTML = response.data.Followers
        tweets_liked_span.innerHTML = response.data.TweetsLiked

        tweets_span.innerHTML = response.data.Tweets
        tweets_read_span.innerHTML = response.data.TweetsRead

        console.log(response)
    } catch (e) {
        console.error(e);
    }
};

// This is to set up our existing projects on reload of site
function main() {
    getTwitterData()
}

main()