export default function () {
    const homepage = Symbol('homepage'),
          endpoints = Symbol('endpoints'),
          headers = Symbol('headers'),
          uname = Symbol('username'),
          token = Symbol('token'),
          userId = Symbol('userId'),
          storage = Symbol('storage'),
          allExist = (...args) => args.reduce((a, b) => !!a && !!b, true),
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
                 set = localStorage.setItem;
                 get = localStorage.getItem;
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
                vals.forEach(v => store(v, creds[v]));
             };
             return {clear, get, store, getAll, setAll};
          },
          User = ({username, token, userId}) => ({
                [uname]: username,
                [token]: token,
                [userId]: userId,
                get username() { return this[uname] },
                get token() { return this[token] },
                get userId() { return this[userId] },
                get loggedIn() { return allExist(this.username, this.token, this.userId) }
                get headers() {
                    return new Headers({'accept': 'application/json',
                                        'x-auth-token': this.user.token,
                                        'x-auth-user': this.user.username})
                }
          }),
          retriever = {
              storer: storer(),
              _user = undefined,
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
                  if (u.loggedIn) {
                      this._user = u;
                      this.storer.setAll(u);
                  }
              },
              getEndpoint(model, method) {
                let ep = this[endpoints][model];
                if (ep !== undefined) {
                    ep = ep[method];
                    if (ep !== undefined) {
                        console.log(ep);
                        return ep
                    }
                }
                return null;
            },
            getResource(model, method="GET") {
                let ep;
                if ((ep = this.getEndpoint(model, method), !!ep)) {
                    return (...args) => {
                        let [epUrl, body] = ep(...args);
                        return {url: `${this[homepage]}${epUrl}`, method, body: (body || '')}
                    }
                }
            },
            retrieve({url, method, body}) {
                console.log(`${method} ${url}`);
                let headers = this.headers,
                    req = new Request(url, {method, headers, body});
                return fetch(req).then(resp => resp.json());
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
                    GET: (user_id) => [`/users/${user_id}/likes`],
                    PUT: (user_id, podcast_id) => [`/users/${user_id}/likes/${podcast_id}`],
                    DELETE: (user_id, podcast_id) => [`/users/${user_id}/likes/${podcast_id}`]
                },
                dislikes: {
                    GET: (user_id) => [`/users/${user_id}/dislikes`],
                    PUT: (user_id, podcast_id) => [`/users/${user_id}/dislikes/${podcast_id}`],
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
                console.log(`ep: ${ep}`);
                if (!!ep) {
                    let u = ep(...args);
                    console.log(u);
                    return this.retrieve(u);
                }
            },
            GET(resource, ...args) { return this.doVerb('GET', resource, ...args) },
            POST(resource, ...args) { return this.doVerb('POST', resource, ...args) },
            PUT(resource, ...args) { return this.doVerb('PUT', resource, ...args) }
        }
        return retriever
    };
