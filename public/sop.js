"use strict";

const API_URL = document.location.origin;


async function make_request(method, url, data) {
    const response = await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    // console.log(result);
    return result
}

async function make_get_request(url, data) {
    return await make_request("GET", url, data)
}

async function make_post_request(url, data) {
    return await make_request("POST", url, data)
}

async function make_put_request(url, data) {
    return await make_request("PUT", url, data)
}


async function uploadImageAndGetUrl(file) {

    const formData = new FormData();
    formData.append('images', file);

    const url = API_URL + "/sop/upload-image";
    const response = await fetch(url, {
        method: "POST",
        body: formData
    });
    const result = await response.json();
    return result
}


function create_quill_sop_data(sopId) {

    return {
        sopId: sopId,
        sopTitle: '',
        sopPurpose: '',
        sopApplication: '',
        quillText: '',
        quillContent: '',
        topic: null,
        topicsNotSelected: false,
        topics: [],
        loading: false,
        public: false,
        incompleteFields: null,
        backendError: null,
        createSOPUrl: API_URL + "/sop/add-sop",
        updateSOPUrl: API_URL + "/sop/update-sop/",
        viewSOPUrl: API_URL + "/sop/view-sop/",
        rateSOPUrl: API_URL + "/sop/rate-sop",
        preFillFields: async function () {
            if (this.sopId == undefined) return

            let resp = await make_get_request("/sop/sop-json/" + sopId);

            if (resp.status == "success") {
                this.sopTitle = resp.content.title;
                this.sopPurpose = resp.content.purpose;
                this.sopApplication = resp.content.application;
                this.quillContent = resp.content.quill;
                this.topics = resp.content.topics;
                this.public = resp.content.public;

                quill.setContents(this.quillContent);

            }
        },
        rateSOP: async function (rating) {

            let data = {
                sop_id: this.sopId,
                rating: rating
            };

            await make_post_request(this.rateSOPUrl, data);

        },
        addTopic: function () {

            if (!this.topic) return;

            if (!this.topics.includes(this.topic)) {
                this.topics.push(this.topic);
                this.topic = null;
            }
        },
        createOrUpdateSOP: async function () {

            this.topicsNotSelected = this.topics ? false : true;
            if (this.topicsNotSelected) {
                return
            }

            this.incompleteFields = [this.sopTitle, this.sopPurpose, this.sopApplication].every((value) => value == '');
            setTimeout(() => {
                if (this.incompleteFields) {
                    this.incompleteFields = null;
                }
            }, 5000);

            if (this.incompleteFields) {
                return
            }

            this.loading = true;

            setTimeout(() => {
                if (this.loading) {
                    this.loading = false;
                }
            }, 5000);


            this.quillText = quill.getText();
            this.quillContent = quill.getContents();

            let data = {
                title: this.sopTitle.trim(),
                purpose: this.sopPurpose.trim(),
                application: this.sopApplication.trim(),
                topics: this.topics,
                content: this.quillText.replace(/\s{3,}/g, ' '),
                quill: this.quillContent,
                public: this.public,
            };

            const URL = this.sopId ? this.updateSOPUrl + this.sopId : this.createSOPUrl;
            const result = await make_request(this.sopId ? "PUT" : "POST", URL, data);

            this.loading = false;

            if (result.status == 'success' && result.content) {
                location.replace(this.viewSOPUrl + result.content);
            } else {
                this.backendError = result.content;
            }
        }
    }
}


function login_data() {
    return {
        email: null,
        password: null,
        loading: false,
        invalidcreds: false,
        loginUrl: API_URL + '/sop/login',
        redirectUrl: API_URL + '/sop/my-account',
        login: async function () {
            this.loading = true;
            setTimeout(() => {
                if (this.loading) {
                    this.loading = false;
                }
            }, 5000);

            const data = {
                email: this.email,
                password: this.password
            };

            const result = await make_post_request(this.loginUrl, data);

            this.loading = false;

            if (result.status == 'success') {
                location.replace(this.redirectUrl);
            } else {
                this.invalidcreds = true;
            }
        }
    }
}

function register_data(inviteToken, company, email) {
    return {
        inviteToken: inviteToken,
        name: null,
        company: company ? company : null,
        email: email ? email : null,
        password: null,
        loading: false,
        confirmpassword: null,
        conditiiacceptate: false,
        registeredemail: false,
        invalidemailorpass: false,
        invalidpass: false,
        invalidconditii: false,
        redirectUrl: API_URL + '/sop/login',
        registerUrl: API_URL + '/sop/register',
        register: async function () {

            this.loading = true;
            setTimeout(() => {
                if (this.loading) {
                    this.loading = false;
                }
            }, 5000);

            this.invalidconditii = !this.conditiiacceptate;
            this.invalidpass = this.password != this.confirmpassword;

            if (this.invalidconditii || this.invalidpass) {
                this.loading = false;
                return
            }

            const data = {
                name: this.name,
                company: this.company,
                email: this.email,
                password: this.password,
            };

            if (this.inviteToken) {
                this.registerUrl = this.registerUrl + "?invite_token=" + this.inviteToken;
            }

            const result = await make_post_request(this.registerUrl, data);
            this.loading = false;

            this.registeredemail = result.content == 'Email is already registered';
            this.invalidemailorpass = result.content == 'Email or password not valid';
            if (result.status == 'success') {
                location.replace(this.redirectUrl);
            }
        }
    }
}

function update_account_data() {
    return {
        files: null,
        loading: false,
        updateAccountUrl: API_URL + '/sop/update-account',
        redirectUrl: API_URL + '/sop/my-account',
        update: async function () {
            this.loading = true;
            setTimeout(() => {
                if (this.loading) {
                    this.loading = false;
                }
            }, 5000);

            let avatarUrl = await uploadImageAndGetUrl(this.files[0]);
            let data = { avatar: avatarUrl };
            let result = await make_put_request(this.updateAccountUrl, data);

            this.loading = false;

            if (result.status == 'success') {
                location.replace(this.redirectUrl);
            }

        }
    }
}


function add_new_user() {
    return {
        email: null,
        role: "Reader",
        loading: false,
        registeredemail: false,
        invitedList: [],
        addUserUrl: API_URL + '/sop/add-new-user',
        addUser: async function () {

            this.loading = true;
            setTimeout(() => {
                if (this.loading) {
                    this.loading = false;
                }
            }, 5000);

            const data = {
                email: this.email,
                role: this.role.toLowerCase(),
            };

            const result = await make_post_request(this.addUserUrl, data);

            if (result.status == "success") {

                let hasEmail = this.invitedList.filter(el => {
                    return (
                        el.email == result.content.email
                        &&
                        el.role.toLowerCase() == result.content.role.toLowerCase()
                    )
                });

                if (hasEmail.length == 0) {

                    this.invitedList.push({
                        email: result.content.email,
                        role: result.content.role,
                        url: result.content.url
                    });

                    navigator.clipboard.writeText(result.content.url);

                    this.email = null;
                }

            } else {
                console.log(result.content);
            }

            this.loading = false;
        }
    }
}


function contact_us_data() {
    return {
        email: null,
        message: null,
        loading: false,
        messageSent: null,
        sendMessageToAdminUrl: API_URL + "/sop/contact",
        sendMessageToAdmin: async function () {
            this.loading = true;

            const data = {
                message: this.message,
                email: this.email,
            };

            const result = await make_post_request(this.sendMessageToAdminUrl, data);

            if (result.status == 'success') {
                this.message = null;
                this.messageSent = true;
                setTimeout(() => this.messageSent = null, 3000);
            } else {
                this.messageSent = false;
                setTimeout(() => this.messageSent = null, 3000);
            }

            this.loading = false;
        }
    }
}
