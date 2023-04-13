<script setup>
import Layout from '../components/Layout.vue';
import UserMethodsAPI from '../api/resources/UserMethods';
import { ref } from 'vue';

const props = defineProps(['id', 'area_name'])
const sectors = ref([]);

const data = await UserMethodsAPI.get_todos(props.id, props.area_name);

sectors.value = data.sectors
</script>

<template>
    <Layout>
        <template v-slot:title>{{ props.id }} - {{ props.area_name }}</template>
        <template v-slot:content>
            <h3>{{ area_name }}</h3>

            <div v-for="sector in sectors" :key="sector.app_url">
                <h3><a :href="$isMobile() ? sector.app_url : sector.url">{{
                    sector.name
                }}</a><a
                        :href="'https://maps.google.com/?q=@' + sector.location[0] + ',' + sector.location[1] + ',10z'">📍</a>
                </h3>
                <div v-for="todo in sector.todos">
                    <div class="flex grow todo_line">
                        <div class="thumb">
                            <img class="thumb" :src="todo.thumb_url" @click="e => e.target.classList.toggle('expand')" />
                        </div>
                        <div class="todo_title">
                            <a :href="$isMobile() ? todo.app_url : todo.url">{{ todo.grade }} {{
                                todo.name
                            }}</a>
                        </div>
                    </div>
                </div>
            </div>

        </template>
    </Layout>
</template>

<style scoped>
img.thumb {
    width: 1.5em;
    height: 1.5em;
}
</style>

<style scoped>
.marker {
    font-size: 0.6em;
    transform-origin: top left;
    z-index: -2;
}

span.tag {
    background-color: #FF4136;
    display: inline-block;
    text-align: center;
    padding: 0.3em;
    font-size: 0.8em;
    border-radius: 50%;
    color: #fff;
    /* overlap a bit */
    margin-left: -0.5em;
}

.right {
    text-align: right;
}

div.todo_line {
    justify-content: stretch;
    margin-bottom: -0.4em;
    margin-top: -0.4em;
}

div.comment_line {
    margin-top: -1.5em;
    justify-content: stretch;
    margin-bottom: -0.5em;
}

div.thumb {
    flex-basis: 2em;
    flex-grow: 0;
}

img.expand {
    width: 6em !important;
    height: 6em !important;

}

div.comment {
    width: auto;
    flex-grow: 1;
}

div.comment span.comment {
    font-size: 0.6em;
}

div.todo_title {
    flex-basis: calc(100% - 8em);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

div.participants {
    flex-basis: 4em;
    text-align: right;
}

svg.youtube {
    height: 1em;
    width: auto;
}

img.thumb {
    height: 1.5em;
    width: 1.5em;
}

img.header {
    width: 100%;
}


div.met_license {
    text-align: right;
    font-size: 0.5em;
}
</style>