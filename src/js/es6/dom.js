export default function () {
    const id = (x) => x;
    return {
        body: document.body,
        weekDays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                   "Friday", "Saturday"],
        models: {
            Podcast: [
                ["id", parseInt],
                ["title", id],
                ["feed_url", id],
                ["homepage", id],
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
        makeTable ({model, result}) {
            let displayModel = this.models[model];
            let table = document.createElement('<table>');
            let header = this.makeHeader(displayModel);
            let content = this.makeContent(displayModel, data);
            document.appendChild(table, header);
            document.appendChild(table, content);
            document.appendChild(this.body, table);
        },
        makeHeader (displayModel) {
            let col;
            let thead = document.createElement('<thead>');
            let tr = document.createElement('<tr>');
            for (col of displayModel) {
                let th = document.createElement('<th>');
                th.textContent = col[0];
                document.appendChild(tr, th);
            }
            document.appendChild(tr, thead);
            return thead;
        },
        makeContent(displayModel, data) {
            let row, key, val;
            let tbody = document.createElement('<tbody>');
            for (row of data) {
                let tr = document.createElement('<tr>');
                for ([label, fn] of displayModel) {
                    let td = document.createElement('<td>');
                    td.textContent = fn(row[label]);
                    document.appendChild(tr, td);
                };
                document.appendChild(tbody, tr);
            }
            return tbody;
        },
        attach(target) {
            Object.assign(target, {makeTable: this.makeTable})
    }
  }
}
