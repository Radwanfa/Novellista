<script lang="ts">
	import { onMount } from 'svelte';
	import { Loader } from '@lucide/svelte';
	let string: string = $state('');
	let id: string = $state('');
	let selected: Node;
	let username = $state('');
	let pending = $state(false);
	let { data } = $props();
	username = data.username;
	string = data.story;
	id = String(data.storyid);

	function getCommonPrefix(a: string, b: string) {
		let i = 0;
		while (i < a.length && i < b.length && a[i] === b[i]) {
			i++;
		}
		return a.slice(0, i);
	}

	onMount(() => {
		let element = document.getElementById(id);
		element!.style.background = 'black';
	});

	async function save() {
		let formdata = new FormData();
		formdata.append('userId', data.id);
		formdata.append('story', string);
		if (id != '') {
			formdata.append('id', id);
		}
		let response = await fetch('http://127.0.0.1:5000/api/save_story', {
			method: 'POST',
			body: formdata
		});
		let result = await response.json();
		if (result.status == 'fail') {
			alert(result.message);
		}
		if (id == '') {
			window.location.href = `/?id=${result.id}`;
		}
	}
	async function request() {
		pending = true;
		let formdata = new FormData();
		formdata.append('text', string);
		let response = await fetch('http://127.0.0.1:5000/api/gen', {
			method: 'POST',
			body: formdata
		});
		let result = await response.text();
		const common = getCommonPrefix(result, string);
		let newText = result.slice(common.length);
		console.log(newText);
		let text = `<br><br><div class=\"text-red-200\">${result}</div><br><br>`;
		string += text;
		pending = false;
	}

	async function getStory() {
		if (!event) return;
		let id = event.srcElement.id;
		window.location.href = `/?id=${id}`;
		let element = document.getElementById(id);
		element!.style.background = 'black';
	}
	function logout() {
		document.cookie = 'session=';
		window.location.href = '/';
	}

	function create() {
		string = '';
		id = '';
		let element = document.getElementById('story');

		save();
	}
</script>

<div class="flex flex-row m-0 h-screen bg-[url(/img/1311862.jpeg)] bg-cover">
	<aside
		class="bg-[#ffffff1a] flex-col backdrop-blur-md border-r-1 rounded-r-xl flex border-white h-screen w-1/4"
	>
		<h1 class="text-white text-6xl mt-6 ml-4">Novellista</h1>
		<h2 class="text-white text-2xl mt-6 ml-2">Welcome, {username}</h2>
		<button
			class="m-4 border-2 border-white rounded-4xl pr-6 pl-6 hover:bg-black text-cyan-50"
			onclick={create}>New story</button
		>
		<div class="flex flex-col" id="story">
			{#each data.stories as id}
				<button
					{id}
					onclick={getStory}
					class="text-white p-2 cursor-pointer mt-1 rounded-[10px] border-0 bg-transparent hover:bg-transparent hover:text-white hover:outline-1 hover:outline-white mb-1"
					>story</button
				>
			{/each}
		</div>
	</aside>
	<div class="m-5 border-l-2 border-white rounded-b-4xl w-full flex flex-col text-base">
		<div
			class="h-11/12 w-full text-xl text-white focus:outline-0 overflow-scroll"
			bind:innerHTML={string}
			contenteditable="true"
		></div>
		<div
			class="w-full h-1/12 border-r-1 border-b-1 rounded-bl-4xl border-t-1 border-white flex justify-end bg-transparent backdrop-blur-sm"
		>
			<button
				class="m-4 border-2 border-white rounded-4xl pr-6 pl-6 hover:bg-black text-cyan-50"
				onclick={logout}>logout</button
			>
			{#if pending == true}
				<Loader size="48" class="self-center text-white animate-spin"/>
			{:else}
			<button
				class="m-4 border-2 border-white rounded-4xl pr-6 pl-6 hover:bg-black text-cyan-50"
				onclick={request}>Suggest</button
			>
			{/if}
			<button
				class="m-4 border-2 border-white rounded-4xl pr-6 pl-6 hover:bg-black text-cyan-50"
				onclick={save}>save</button
			>
		</div>
	</div>
</div>
