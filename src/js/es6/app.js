const Retriever = () => {
    const homepage = Symbol('homepage');
    const endpoints = Symbol('endpoints');
    const retriever = {
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
        if ((ep = this.getEndpoint(model, method), ep !== null)) {
            return (...args) => {
                ep = ep(...args);
                return {url: `${this[homepage]}${ep}`, method}
            }
        }
    },
    retrieve({url, method}) {
        return new Promise((resolve, reject) => {
            const req = new XMLHttpRequest()
            req.open(method, url)
            req.onload = () => {
                if (req.status == 200) {
                    resolve(JSON.parse(req.responseText))
                } else {
                    reject(Error(req.status, JSON.parse(req.responseText)))
                }
            }
            req.onerror = () => {
                reject(Error(-1))
            }
            req.send()
        })
    },
    [homepage]: "http://localhost:8000",
    [endpoints]: {
        categories: {
            GET: (category_id) => `/categories/${category_id}`
        },
        podcasts: {
            GET: (podcast_id) => `/podcasts/${podcast_id}`
        },
        likers: {
            GET: (podcast_id) => `/podcasts/${podcast_id}/likers`
        },
        dislikers: {
            GET: (podcast_id) => `/podcasts/${podcast_id}/dislikers`
        },
        podcast_categories: {
            GET: (podcast_id) => `/podcasts/${podcast_id}/categories`
        },
        users: {
            GET: (user_id) => `/users/${user_id}`
        },
        likes: {
            GET: (user_id) => `/users/${user_id}/likes`,
            PUT: (user_id, podcast_id) => `/users/${user_id}/likes/${podcast_id}`
        },
        dislikes: {
            GET: (user_id) => `/users/${user_id}/dislikes`,
            PUT: (user_id, podcast_id) => `/users/${user_id}/likes/${podcast_id}`
        },
        login: {
            POST: () => "/login"
        },
        search: {
            GET: (query) => {
                const query_components = ["page", "title", "author", "homepage",
                                          "day_of_week", "day_of_month",
                                          "length", "category", "published_since"];
                let ep = "/search/podcasts";
                let k, val;
                ep += "?";
                for (k of query_components) {
                    if ((val = query[k], val !== undefined)) {
                        ep = `${ep}${k}=${val}&`;
                    }
                }
                return ep.slice(0, -1);
            }
        }
    }
    }
    return retriever
}

const Dom = () => {
    const id = (x) => x;
    const weekDays = Symbol('weekDays');
    const models = Symbol('models');
    const makeHeader = Symbol('makeHeader');
    const makeContent = Symbol('makeContent');
    const dom = {
        makeTable(model, result) {
            let preexisting = document.getElementById('tgt');
            if (preexisting !== null) {
                document.body.removeChild(preexisting);
            };
            let displayModel = this[models][model];
            let table = document.createElement('table');
            table.setAttribute('id', 'tgt');
            let header = this[makeHeader](displayModel);
            let content = this[makeContent](displayModel, result);
            table.appendChild(header);
            table.appendChild(content);
            document.body.appendChild(table);
        },
        [weekDays]: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday"],
        [models]: {
            Podcast: [
                ["id", parseInt],
                ["title", id],
                ["feed_url", id],
                ["language", id],
                ["episode_count", parseInt],
                ["explicit", Boolean],
                ["summary", id]
            ],
            Episode: [
                ["id", parseInt],
                ["date", id],
                ["title", id],
                ["podcast_id", parseInt],
                ["week_day", (wd) => this.weekDays[wd]],
                ["day_of_month", id]
            ],
            Category: [
                ["id", parseInt],
                ["name", id]
            ],
            User: [
                ["id", parseInt],
                ["name", id],
                ["email", id],
                ["public", Boolean]
            ]
        },
        [makeHeader](displayModel) {
            let col, th;
            const thead = document.createElement('thead');
            const tr = document.createElement('tr');
            for (col of displayModel) {
                th = document.createElement('th');
                th.textContent = col[0];
                tr.appendChild(th);
            }
            thead.appendChild(tr);
            return thead;
        },
        [makeContent](displayModel, data) {
            let fn, label, key, row, td, tr, val;
            const tbody = document.createElement('tbody');
            for (row of data) {
                tr = document.createElement('tr');
                for ([label, fn] of displayModel) {
                    td = document.createElement('td');
                    td.textContent = fn(row[label]);
                    tr.appendChild(td);
                };
                tbody.appendChild(tr);
            }
            return tbody;
        },
  }
    return dom;
}


const manager = () => {
    const Manager = {
        dom: Dom(),
        retriever: Retriever(),
        renderQuery(resource, method, ...args) {
            let ep = this.retriever.getResource(resource, method);
            if (ep === null) {
                console.log(`no such ep: ${resource} ${method}`);
            } else {
                let url = ep(...args);
                console.log(url);
                this.retriever.retrieve(url).then(
                    ({model, result}) => {
                        this.dom.makeTable(model, result);
                    },
                    (err) => console.log(err))
            }
        },
        GET(resource, ...args) {
            this.renderQuery(resource, "GET", ...args)
        }
    }
    return Manager;
}

const init = () => {
    document.manager = manager();
};
init();
