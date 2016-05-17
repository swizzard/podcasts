export default function () {
    const homepage = Symbol('homepage'),
          endpoints = Symbol('endpoints'),
          headers = Symbol('headers'),
          _username = Symbol('username'),
          _token = Symbol('token'),
          _userId = Symbol('userId'),
          storage = Symbol('storage'),
          allExist = (...args) => args.reduce((a, b) => !!a && !!b, true),
          methods = ['GET', 'POST', 'PUT', 'DELETE'],
          storer = () => {
             let hasStorage = false,
                 vals = ['username', 'token', 'userId'],
                 clear, get, getAll, set, setAll;
             if (!!localStorage) {
                 try {
                     localStorage.setItem('test', 'test');
                     localStorage.removeItem('test');
                     hasStorage = true;
                 } catch(e) {}
             };
             console.log(`using ${hasStorage ? 'localStorage' : 'cookies'}`);
             if (hasStorage) {
                 clear = () => {
                     vals.forEach(v => localStorage.removeItem(v));
                 },
                 set = localStorage.setItem.bind(localStorage);
                 get = localStorage.getItem.bind(localStorage);
             } else {
                 clear = () => {
                     vals.forEach(v => document.cookie = `${v}=`);
                 },
                 set = (k, v) => document.cookie = `${k}=${v}`,
                 get = k => {
                    let p = new RegExp(`${k}=([\\w\\d_]+)`), v = null, m;
                    if ((m = document.cookie.match(p), !!m)) {
                        v = m[1];
                    };
                    return v
                 };
             };
             getAll = () => {
                 let res = {};
                 vals.forEach(v => res[v] = get(v));
                 return res;
             };
             setAll = creds => {
                vals.forEach(v => set(v, creds[v]));
             };
             return {clear, get, set, getAll, setAll};
          },
          User = ({username, token, userId}) => ({
                [_username]: username,
                [_token]: token,
                [_userId]: userId,
                get username() { return this[_username] },
                get token() { return this[_token] },
                get userId() { return this[_userId] },
                get loggedIn() { return allExist(this.username, this.token, this.userId) },
                get headers() {
                    return new Headers({'accept': 'application/json',
                                        'x-auth-token': this.token,
                                        'x-auth-user': this.username})
                }
          }),
          retriever = {
            storer: storer(),
            _user: undefined,
            get user() {
                if (!this._user) {
                    let u = User(this.storer.getAll());
                    if (u.loggedIn) {
                        this._user = u;
                    }
                }
                return this._user;
            },
            set user(creds) {
                let u = User(creds);
                this._user = u;
                this.storer.setAll(u);
            },
            getEndpoint(model, method) {
                let ep = this[endpoints][model];
                if (ep !== undefined) {
                    ep = ep[method];
                    if (ep !== undefined) {
                        return ep
                    }
                }
                return null;
            },
            getResource(model, method="GET") {
                let ep;
                if ((ep = this.getEndpoint(model, method), !!ep)) {
                    return (...args) => {
                        let [epUrl, body] = ep(...args),
                            res = {url: `${this[homepage]}${epUrl}`, method};
                        if (method === 'POST' || method === 'PUT') {
                            res.body = body;
                        };
                        return res
                    }
                }
            },
            retrieve({url, method, body}) {
                console.log(`${method} ${url}`);
                let headers = this.user.headers,
                    args = {url, method, headers},
                    req;
                    if (method === 'POST' || method === 'PUT') {
                        args.body = body;
                    }
                    req = new Request(url, args);
                    return fetch(req)
                        .then(r => {
                            if (r.status !== 200) {
                                throw new Error(r.statusText);
                            } else {
                                return r.json()
                            }
                    });
            },
            [homepage]: "http://localhost:8000",
            [endpoints]: {
                categories: {
                    GET: (category_id) => [`/categories/${category_id}`]
                },
                podcasts: {
                    GET: (podcast_id) => [`/podcasts/${podcast_id}`]
                },
                likers: {
                    GET: (podcast_id) => [`/podcasts/${podcast_id}/likers`]
                },
                dislikers: {
                    GET: (podcast_id) => [`/podcasts/${podcast_id}/dislikers`]
                },
                podcast_categories: {
                    GET: (podcast_id) => [`/podcasts/${podcast_id}/categories`]
                },
                users: {
                    GET: (user_id) => [`/users/${user_id}`],
                    POST: (user) => ['/users', JSON.stringify(user)]
                },
                likes: {
                    GET: (user_id) => [`/users/${user_id}/podcasts/likes`],
                    PUT: (user_id, podcast_id) => [`/users/${user_id}/podcasts/likes/${podcast_id}`],
                    DELETE: (user_id, podcast_id) => [`/users/${user_id}/podcasts/likes/${podcast_id}`]
                },
                dislikes: {
                    GET: (user_id) => [`/users/${user_id}/podcasts/dislikes`],
                    PUT: (user_id, podcast_id) => [`/users/${user_id}/podcasts/dislikes/${podcast_id}`],
                    DELETE: (user_id, podcast_id) => [`/users/${user_id}/dislikes/${podcast_id}`]
                },
                login: {
                    POST: (creds) => ["/login", JSON.stringify(creds)]
                },
                search: {
                    POST: (query) => ["/search/podcasts", JSON.stringify(query)]
                }
            },
            doVerb(verb, resource, ...args) {
                let ep = this.getResource(resource, verb);
                if (!!ep) {
                    let u = ep(...args);
                    return this.retrieve(u);
                }
            },
        };
        methods.map(method => {retriever[method] = retriever.doVerb.bind(retriever, method)});
        return retriever
    };
