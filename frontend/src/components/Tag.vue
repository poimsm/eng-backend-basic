<template>
	<div class="tag noselect" :class="{ active: isActive }">
		{{ name }}
	</div>
</template>

<script>
export default {
	props: {
		isActive: Boolean,
		name: String,
	},
};
</script>

<style scoped>
.tag {
	border-radius: 15px;
	height: 35px;
	display: block;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #444;
	outline: 1px solid #444;
	min-width: 70px;
	padding: 0 10px;
	cursor: pointer;
}

.active {
	border: 0px;
	background: red;
	color: white;
	font-weight: 500;
	outline: none;
}

</style>
