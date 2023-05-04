<template>
	<div>
        <div style="position:fixed;top:0;left:0;width:250px">
             <div style="font-size:24px;padding: 20px 100px">
                {{copiedWords.length}}</div>
            {{copiedWords}}
        </div>
        
        <div style="display:flex;flex-wrap:wrap;padding-left:300px;width:800px">
            <div style="width: 600px; display:flex;justify-content:space-around">
            <MainBtn @click="onRandomizeWords" title="Randomize Words" />
            <MainBtn @click="onSortWords" title="Sort Words" />
        </div>
      <!-- <div>
         <div style="width:600px"> -->
         <tempalte v-for="(word, i) in words" :key="i">
            <div @click="onCopy(word, i)" style="margin: 10px">
                <Tag :isActive="word.copied" :name="word.word"/>
            </div>
        </tempalte>
       <!-- </div>
      </div> -->

        
    </div>
    </div>
</template>

<script>
import Tag from "../components/Tag.vue";
import MainBtn from "../components/MainBtn.vue";

import { wordsData } from "../js/words02";
// import { fetchCategories } from "../js/network";

export default {
	props: {
		msg: String,
	},
	data() {
		return {
            words: [],
            copiedWords: []
			// words: wordsData
		};
	},
	methods: {
        onCopy(word, i) {
            this.words[i].copied = !this.words[i].copied
            // const found = this.copiedWords.indexOf(word.word)
            
            if(!this.words[i].copied) {
                this.copiedWords.pop()
            } else {
                this.copiedWords.push(word.word)
            }
            
        },
        shuffle(array) {
            let currentIndex = array.length,  randomIndex;
            // While there remain elements to shuffle.
            while (currentIndex != 0) {
            // Pick a remaining element.
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;
            // And swap it with the current element.
            [array[currentIndex], array[randomIndex]] = [
                array[randomIndex], array[currentIndex]];
            }
            return array;
        },
        async onRandomizeWords() {
            this.words = []
            await new Promise((r) => setTimeout(r, 500));
            const clone = JSON.parse(JSON.stringify(wordsData));
            let words_temp = this.shuffle(clone);
            this.words = words_temp.map(w => ({
                copied: false,
                word: w
            }));
        },
        async onSortWords() {
            this.words = []
            await new Promise((r) => setTimeout(r, 500));
            this.words = wordsData.map(w => ({
                copied: false,
                word: w
            }));
        },
        onClick() {
            console.log('clicked');
        }
	},
	components: {
		Tag,
        MainBtn,
	},
};
</script>

<style scoped>
</style>
