import Retriever from './retriever';
import Tabler from './tabler';
import podSearch from './searcher';
import UserWidget from './user';

const retriever = document.retriever = Retriever(),
      tabler = Tabler($("#bottom"));
let tp = $('#top'),
    user = $('#user'),
    bottom = $('#bottom');
podSearch(retriever, tabler, tp);
UserWidget(retriever, tabler, user, bottom);

