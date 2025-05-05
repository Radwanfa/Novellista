<div class="flex flex-row">
	<aside class="bg-amber-600 border-r-2 flex border-amber-200 h-screen w-1/4">&nbsp;</aside>
	<div class="m-5 border-l-2 border-amber-300 w-full flex flex-col text-base">
		<div
			class="h-11/12 w-full text-xl focus:outline-0"
			bind:innerHTML={string}
			contenteditable="true"
		></div>
		<div class="w-full h-1/12 border-r-2 border-b-2 border-t-2 border-amber-300 flex justify-end">
			<button
				class="m-4 border-2 border-amber-200 pr-6 pl-6 hover:bg-amber-950 text-cyan-50"
				onclick={request}>Suggest</button
			>
		</div>
	</div>
</div>
<script lang="ts">
	let string: string = $state('text');
	let username;
	let { data } = $props();
	username = data.username;
	async function request() {
		console.log(string);
		let formdata = new FormData();
		formdata.append('text', string);
		let response = await fetch('http://127.0.0.1:5000/api/gen', {
			method: 'POST',
			body: formdata
		});
		let result = await response.text();
		string += result;
	}
</script>