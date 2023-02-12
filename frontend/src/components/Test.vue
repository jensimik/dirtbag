<script setup>
import TestMethodsAPI from '../api/resources/TestMethods.js';
import { ref } from 'vue';

const data = ref([]);

data.value = await TestMethodsAPI.index("Albarracin");
</script>

<template>
  <div v-for="(todos, sector_name) in data">
    <h2><a :href="todos[0].sector_url">{{ sector_name }}</a></h2>
    <ul>
      <li v-for="todo in todos"><a :href="todo.app_url"><img :src="todo.thumb_url" /></a>
        <a :href="todo.url">{{ todo.name }}</a> ({{ todo.grade }}) {{
  todo.user_ids
        }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}

li img {
  width: 1.5em;
  height: 1.5em;
}
</style>