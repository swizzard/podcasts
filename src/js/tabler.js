export default function (retriever, target) {
    const makeEmpty = name => $(`<${name}></${name}>`),
          model = (name, fields) => {
            let k, f;
            const res = {
                name: name,
                data: {},
                order: [],
                get showLikes() {
                    return (this.name === 'podcast' && retriever.user.loggedIn);
                },
                header() {
                    let col;
                    const thead = makeEmpty('thead');
                    const tr = makeEmpty('tr');
                    for (col of this.order) {
                        let th = makeEmpty('th');
                        th.text(col);
                        th.appendTo(tr);
                    };
                    if (this.showLikes) {
                        let likeTh = makeEmpty('th'),
                            dislikeTh = makeEmpty('th');
                        likeTh.text('like');
                        dislikeTh.text('dislike');
                        tr.append(likeTh, dislikeTh);
                    };
                    thead.append(tr);
                    return thead;
                },
                rows(data) {
                    const tbody = makeEmpty('tbody');
                    let row, tr, col;
                    for (row of data) {
                        tr = makeEmpty('tr');
                        for (col of this.order) {
                            let v = row[col],
                                td = makeEmpty('td');
                            this.data[col](v, td).appendTo(tr);
                        };
                        if (this.showLikes) {
                            makeEmpty('td').append($('<button class="btn btn-success like" ' +
                                                     `data-id="${row.id}" data-ep="likes">`  +
                                                     'like this</button>')).appendTo(tr);
                            makeEmpty('td').append($('<button class="btn btn-warning like" ' +
                                                     `data-id="${row.id}" data-ep="dislikes">` +
                                                     'dislike this</button>')).appendTo(tr);
                        };
                        tbody.append(tr);
                    }
                    return tbody;
                }
            };
            for ([k, f] of fields) {
                res.order.push(k);
                res.data[k] = f;
            };
            return res;
          },
          userId = retriever.user.userId,
          makeLink = (url, link) => $(`<a href="${url}">${link === undefined ? url : link}</a>`),
          setText = f => (val, node) => node.text(f(val)),
          setParseInt = setText(parseInt),
          setId = setText(x => x),
          setTrim = n => setText(t => (t.length >= n ? `${t.slice(0, n)}...` : t)),
          setBool = setText(Boolean),
          weekDays = Symbol('weekDays'),
          models = Symbol('models'),
          getLikes = () => {
              let likes = new Set(),
                  res;
              retriever.GET(name, userId)
                  .then(js => {
                      if
              ['likes', 'dislikes'].map(name => {
                retriever.GET(name, userId)
                    .then(js => {
                        console.log(js);
                        if ((res = js.result, !!res)) {
                            res.map(p => out[name].add(p.id));
                        }
                    })
              });
              return out;
          },
          likeCB = e => {
            let target = $(e.target),
                ep = target.data('ep'),
                podcastId = target.data('id'),
                toRemove = target.hasClass('active');
            retriever[toRemove ? 'DELETE' : 'PUT'](ep, userId, podcastId)
                .then(js => {
                    if (!js || !js.result || !js.result[0].success) {
                        throw new Error('bad response from server');
                    } else {
                        target[toRemove ? 'removeClass' : 'addClass']('active');
                        target.attr('aria-pressed', `${!toRemove}`);
                    }
                })
                .catch(err => { $(`<p class="bg-danger">${err}</p>`)
                                .appendTo(target); });
          },
          clickLikes = () => {
              const likeIds = getLikes();
              const inLikes = idx => ({like: likeIds.likes.has(idx),
                                       dislike: likeIds.dislikes.has(idx)});
              $('.like').map((_, e) => {
                let idx = e.dataset.id,
                    ep = e.dataset.ep,
                    il = inLikes(idx);
                if (inLikes(e.dataset.id)[e.dataset.ep]) {
                      $(e).addClass('active');
                      $(e).attr('aria-pressed', 'true');
                  };
              })
          },
          tabler = {
            target: target,
            makeTable(model, result) {
                let tableId = 'resTable',
                    likes, dislikes;
                $(`#${tableId}`).remove();
                let displayModel = this[models][model];
                $(`<table id="${tableId}" ` +
                  'class="table table-hovertable-bordered"></table>')
                    .append(displayModel.header())
                    .append(displayModel.rows(result))
                    .appendTo(this.target);
                if (displayModel.showLikes) {
                    clickLikes()
                };
                $(`#${tableId}`).on('click', '.like', likeCB);
            },
            clear() {
                this.target.empty();
            },
            [weekDays]: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday"],
            [models]: {
                Podcast: 
                    model('podcast',
                        [
                            ["id", setParseInt],
                            ["title", setId],
                            ["feed_url", (val, node) => node.append(makeLink(val))],
                            ["language", setId],
                            ["episode_count", setParseInt],
                            ["explicit", setBool],
                            ["summary", setTrim(100)]
                        ]),
                Episode: 
                    model('episode',
                        [
                            ["id", setParseInt],
                            ["date", setId],
                            ["title", setId],
                            ["podcast_id", setParseInt],
                            ["week_day", setText((wd) => this.weekDays[wd])],
                            ["day_of_month", setId]
                        ]),
                Category: 
                    model('category',
                        [
                            ["id", setParseInt],
                            ["name", setId]
                        ]),
                User: 
                    model('user',
                        [
                            ["id", setParseInt],
                            ["name", setId],
                            ["email", setId],
                            ["public", setBool]
                        ])
            },
    };
        return tabler;
};
