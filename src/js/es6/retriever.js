export default function () {
   return {
    getResource(model, method="GET") {
        let ep;
        if ((ep = this.endpoints[model][method], ep !== undefined)) {
            return (...args) => {
                return {url: `${this.homepage}${ep(...args)}`, method}
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
    attach(target) {
        Object.assign(target, {getResource: this.getResource, retrieve: this.retrieve})
    },
    homepage: "http://localhost:8000",
    endpoints: {
        categories: {
            GET: {
                endpoint: (category_id) => `/categories/${category_id}`
            }
        },
        podcasts: {
            GET: {
                endpoint: (podcast_id) => `/podcasts/${podcast_id}`
            }
        },
        likers: {
            GET: {
                endpoint: (podcast_id) => `/podcasts/${podcast_id}/likers`
            }
        },
        dislikers: {
            GET: {
                endpoint: (podcast_id) => `/podcasts/${podcast_id}/dislikers`
            }
        },
        podcast_categories: {
            GET: {
                endpoint: (podcast_id) => `/podcasts/${podcast_id}/categories`
            }
        },
        users: {
            GET: {
                endpoint: (user_id) => `/users/${user_id}`
            }
        },
        likes: {
            GET: {
                endpoint: (user_id) => `/users/${user_id}/likes`
            },
            PUT: {
                endpoint:
                    (user_id, podcast_id) => `/users/${user_id}/likes/${podcast_id}`
            }
        },
        dislikes: {
            GET: {
                endpoint: (user_id) => `/users/${user_id}/dislikes`
            },
            PUT: {
                endpoint:
                    (user_id, podcast_id) => `/users/${user_id}/likes/${podcast_id}`
            }
        },
        login: {
            POST: {
                endpoint: () => "/login"
            }
        },
        search: {
            GET: {
                endpoint: (query={}) => {
                    let query_components = ["title", "author", "homepage",
                                            "day_of_week", "day_of_month",
                                            "length", "category", "published_since"];
                    let ep = "/search/podcasts";
                    let val;
                    if (Object.getOwnPropertyNames(query).length === 0) {
                        return ep;
                    } else {
                        ep += "?"
                        for (let k of query_components) {
                            if ((val = query[k], val !== undefined)) {
                                ep += `${k}=${val}&`
                            }
                            return ep.slice(0, -1)
                        }
                    }
                }
            }
        }
    }
  }
}
