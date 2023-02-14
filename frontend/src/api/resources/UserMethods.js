import { APISettings } from '../config.js';

export default {

    async sync_27crags(user_id) {
        const response = await fetch(APISettings.baseURL + '/user/' + user_id, {
            method: 'POST',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async sync_done(user_id) {
        const response = await fetch(APISettings.baseURL + '/user/' + user_id + '/sync_done', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async areas(user_id) {
        const response = await fetch(APISettings.baseURL + '/user/' + user_id + '/areas', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
}