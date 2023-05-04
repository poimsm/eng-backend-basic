<template>
	<div>
		<div v-for="(cat, i) in categories" :key="i + '_cat'" style="display: flex">
			<div @click="toggleCat(i)" class="cat">
				<Category :name="cat.name" :isActive="cat.isActive" />
			</div>
			<div class="tags-box">
				<div v-for="(tag, j) in cat.tags" :key="j + '_tag'">
					<div @click="toggleTag(i, j)" style="margin-right: 20px">
						<Tag :name="tag.name" :isActive="tag.isActive" />
					</div>
				</div>
			</div>
		</div>
		<div class="menu-box">
			<div class="found-words">13 Questions Found!!</div>
			<div @click="selectAllWords()" class="select-all-words noselect">
				<span v-if="!allQuestionsSelected"> 🔘 </span>
				<span v-else> 🟣 </span>
				Select all questions
			</div>
			<MainBtn @click="onQuestionFilter" title="Filter Questions" />
		</div>

		<div class="questions-box">
			<div v-for="(question, idx) in questions" :key="idx">
				<div @click="toggleQuestion(idx)" style="margin-bottom: 25px">
					<Question :name="question.question" :isActive="question.isActive" />
				</div>
			</div>
		</div>

		<div class="menu-box">
			<div class="select-word-box">
				<div @click="onBackWord" class="noselect word-btn">🔙</div>
				<div class="word-box">
					{{ selectedWord.word }}
					<div class="word-type">{{ selectedWord.type }}</div>
				</div>
				<div @click="onNextWord" class="noselect word-btn">🔜</div>
			</div>
			<MainBtn @click="onCreateWord" title="🔗 Make Link" />
		</div>
	</div>
</template>

<script>
import Tag from "../components/Tag.vue";
import Category from "../components/Category.vue";
import MainBtn from "../components/MainBtn.vue";
import Question from "../components/Question.vue";
import { categories, questions, words } from "../js/dummy";
import { fetchCategories } from "../js/network";

export default {
	props: {
		msg: String,
	},
	data() {
		return {
			categories: categories,
			questions: questions,
			allQuestionsSelected: false,
			words: words,
			selectedWord: words[0],
			wordIndex: 0,
		};
	},
	methods: {
		async fetchCats() {
			this.categories = await fetchCategories();
		},
		onQuestionFilter() {},
		onCreateWord() {},
		onBackWord() {
			if (this.wordIndex == 0) return;
			this.wordIndex -= 1;
			this.selectedWord = this.words[this.wordIndex];
		},
		onNextWord() {
			if (this.wordIndex == this.words.length - 1) return;
			this.wordIndex += 1;
			this.selectedWord = this.words[this.wordIndex];
		},
		selectAllWords() {
			this.allQuestionsSelected = !this.allQuestionsSelected;

            for (let i = 0; i < this.questions.length; i++) {
                this.questions[i].isActive = this.allQuestionsSelected                
            }
		},
		toggleCat(idx) {
			this.categories[idx].isActive = !this.categories[idx].isActive;

			if (!this.categories[idx].isActive) {
				for (let i = 0; i < this.categories[idx].tags.length; i++) {
					this.categories[idx].tags[i].isActive = false;
				}
			}
		},
		toggleTag(catIdx, tagIdx) {
			this.categories[catIdx].tags[tagIdx].isActive =
				!this.categories[catIdx].tags[tagIdx].isActive;
		},
		toggleQuestion(i) {
			this.questions[i].isActive = !this.questions[i].isActive;
		},
	},
	components: {
		Tag,
		Category,
		MainBtn,
		Question,
	},
};
</script>

<style scoped>
.cat {
	padding: 15px 30px;
	width: 300px;
}

.tags-box {
	padding: 15px 30px;
	display: flex;
	width: 600px;
}

.btn-box {
	padding: 30px;
	padding-right: 200px;
	display: flex;
	justify-content: flex-end;
}

.menu-box {
	padding: 30px;
	padding-right: 200px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.questions-box {
	padding: 30px;
	padding-right: 200px;
}

.select-word-box {
	display: flex;
	align-items: center;
}

.word-btn {
	cursor: pointer;
	font-size: 40px;
}

.word-box {
	padding: 0 20px;
	width: 100px;
	text-align: center;
}

.word-type {
	font-size: 12px;
	color: #666;
}

.select-all-words {
	cursor: pointer;
	color: #5532b8;
	font-weight: 600;
}

.found-words {
	color: #5532b8;
	font-weight: 600;
}
</style>
