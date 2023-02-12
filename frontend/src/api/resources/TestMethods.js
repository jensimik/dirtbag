import { APISettings } from '../config.js';

export default {

    async index(area_name) {
        const response = await fetch(APISettings.baseURL + '/todos/' + area_name, {
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