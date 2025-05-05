import { redirect } from '@sveltejs/kit';

export async function load({ cookies, fetch }) {
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
    let result = await response.json()
    
    return {
        username: result.username
    };
}