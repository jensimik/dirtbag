import { APISettings } from '../config.js';

export default {

    async get(sector_name) {
        const response = await fetch(APISettings.baseURL + '/sector/' + sector_name + '/forecast', {
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