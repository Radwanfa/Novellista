import { redirect } from '@sveltejs/kit';
import { json } from '@sveltejs/kit';

export async function load({ cookies, fetch, url }) {
    let session = cookies.get('session');
    if (!session) {
        redirect(307, "/login")
    }
    let formdata = new FormData();
	formdata.append("session", String(session));

    let response = await fetch('http://127.0.0.1:5000/api/get_session', {
		method: "POST",
		body: formdata
	});
    let result = await response.json();

    let id = result.id;
    let username = result.username;

    response = await fetch('http://127.0.0.1:5000/api/get_stories', {
        method: "POST",
        headers: {
            "userId": id
        }
    });
    result = await response.json();
    let stories = result.stories;
    let storyid;
    let content;
    if (url.searchParams.get("id") != undefined) {
        storyid = url.searchParams.get("id");
        response = await fetch(`http://127.0.0.1:5000/api/get_story?id=${storyid}`, {
            method: "GET"
        });
        result = await response.json();
    } else {
        storyid = undefined;
    }

    
    
    return {
        username: username,
        id: id,
        stories: stories,
        storyid: storyid,
        story: result.story
    };
}