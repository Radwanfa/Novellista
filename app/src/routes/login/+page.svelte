<script lang="ts">
	let loginType = $state(false);
	let username = $state("");
	let password = $state("");
	let Rpassword = $state("");

	async function handle() {
		let formdata = new FormData();
		if (loginType) {
			formdata.append("username", username);
			formdata.append("password", password);
			formdata.append("Rpassword", Rpassword);
			let response = fetch('http://127.0.0.1:5000/api/register', {
				method: "POST",
				body: formdata
			});
			let result = (await response).json()
			alert(result);
		} else {
			formdata.append("username", username);
			formdata.append("password", password);
			let response = fetch('http://127.0.0.1:5000/api/login', {
				method: "POST",
				body: formdata
			});
			let result = (await response).json()
			alert(result);
		}
	}
</script>

<div
	class="m-0 flex justify-center items-center h-screen bg-[url(/img/background-image.jpg)] bg-cover"
>
	<div
		class="w-1/6 relative z-1 bg-[#ffffff1a] shadow-md border-1 border-solid border-[#fff] rounded-[10px] before:content-[''] before:absolute before:w-full before:h-full before:rounded-[10px] before:backdrop-blur-[5px] before:-z-1"
	>
		<div class="max-w-3/4 text-center" style="margin: 0 auto;">
			{#if loginType == true}
				<h1 class="text-white mt-8 -mb-5 text-3xl">Register</h1>
			{:else}
				<h1 class="text-white mt-8 -mb-5 text-3xl">Login</h1>
			{/if}

			<div class="flex flex-col mt-[20px]">
				<input
					type="text"
					name="username"
					required
					placeholder="username"
					class="p-2 mt-6 bg-transparent text-white text-m rounded-[10px] border-white border-1 placeholder:text-white focus:outline-0"
					bind:value={username}
				/>
				<input
					type="password"
					name="password"
					required
					placeholder="password"
					class="p-2 mt-6 bg-transparent text-white text-m rounded-[10px] border-1 border-white placeholder:text-white focus:outline-0"
					bind:value={password}
				/>
				{#if loginType == true}
					<input
						type="password"
						name="repeat password"
						required
						placeholder="repeat password"
						class="p-2 mt-6 bg-transparent text-white text-m rounded-[10px] border-1 border-white placeholder:text-white focus:outline-0"
						bind:value={Rpassword}
					/>
				{/if}
				<div class="flex items-center mt-4 text-m text-white">
					<input type="checkbox" bind:checked={loginType} name="register" class="mr-1 mt-0" />
					<label for="register">register instead</label>
				</div>
				<button
					class="text-black p-2 cursor-pointer mt-4 rounded-[10px] border-0 bg-white hover:bg-transparent hover:text-white hover:outline-1 hover:outline-white mb-16"
					onclick={handle}
					>submit</button
				>
			</div>
		</div>
	</div>
</div>
