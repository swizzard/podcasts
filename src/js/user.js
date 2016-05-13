export default function(retriever, tabler, target, bigTarget) {
    let init;
    const uname = () => {
            const unames = ['heynongman', 'hanmahb00gie', 'mailkimplov3r', 'freeAdnan',
                            'boomer_lives', 'tracysjoketime'];
            return unames[Math.floor(Math.random() * unames.length)]
          },
          userWidget = $('<div class="row" id="userwidget"></div>'),
          uwidgetClasses = "col-sm-2 pull-right user-widget",
          logInWidget = $(`<div class="${uwidgetClasses}" id="loginWidget">` +
                           '<form class="form-group"><div class="form-group">' +
                           '<label for="username">Username: </label>' +
                           '<input type="text" class="form-control" id="username" ' +
                           `placeholder="${uname()}" /></div>\n` +
                           '<div class="form-group"><label for="password">Password: ' +
                           '</label><input type="password" class="form-control" ' +
                           'id="password" placeholder="password" /></div>' +
                           '<div><button type="button" id="log-in" ' +
                           'class="btn btn-default btn-sm">Log In</button>' +
                           '<button type="button" id="sign-up" ' +
                           'class="btn btn-default btn-sm">Sign Up</button></form>' +
                           '</div></div>'),
          getLoggedInWidget = () => $(`<div class="${uwidgetClasses}" id="logged-in">` +
                                      `<p><strong>Username: </strong> ${retriever.username}</p>` +
                                      '<p id="user-actions">' +
                                      '<button class="btn btn-default btn-xs" id="profile">Profile</button>' +
                                      '&nbsp;<button class="btn btn-success btn-xs" id="likes">Likes' +
                                      '</button>&nbsp;<button class="btn btn-danger btn-xs" id="logout">' +
                                      'Log Out</button></p></div>'),
          signUpWidget = $(`<div class="col-md-8" id="signupWidget">` +
                            '<form><div class="form-group">' +
                            '<label for="signup-username">Username: </label>' +
                            '<input type="text" id="signup-username" ' +
                            `class="form-control" placeholder="${uname()}"/>` + 
                            '</div><div class="form-group">' +
                            '<label for="signup-pw1">Password: </label>' +
                            '<input type="password" id="signup-pw1" ' +
                            'class="form-control" placeholder="password" />' +
                            '</div><div class="form-group">' +
                            '<label for="signup-pw2">Password (again): </label>' +
                            '<input type="password" id="signup-pw2" ' +
                            'class="form-control" placeholder="password (again)" />' +
                            '</div><div class="form-group">' +
                            '<label for="signup-email">Email: </label>' +
                            '<input type="email" id="signup-email" ' +
                            'class="form-control" placeholder="you@example.com" />' +
                            '</div><div class="checkbox"><label>' +
                            '<input type="checkbox" id="signup-public"> Make profile public' +
                            '</label></div><button class="btn btn-primary" id="go">Go!</button>' +
                            '</form></div>'),
          signUp = e => {
              let target = $(e.target).parents('form'),
                  username = target.find('#signup-username'),
                  username_val = username.val(),
                  pw1 = target.find('#signup-pw1'),
                  pw1_val = pw1.val(),
                  pw2 = target.find('#signup-pw2'),
                  pw2_val = pw2.val(),
                  email = target.find('#signup-email'),
                  email_val = email.val(),
                  pub = target.find('#signup-public'),
                  pub_val = pub.val(),
                  out = {},
                  user_id,
                  creds,
                  showErr = (elem, msg) => {
                      console.log(`err: ${msg}`);
                      let errMsg = $(`<p class="bg-danger err">${msg}</p>`);
                      elem.after(errMsg);
                      elem.on('focus', () => errMsg.remove());
                  },
                  email_pat = /[A-Za-z0-9_\-\.]+@[A-Za-z0-9_\-\.]+(\.[a-z]{2,})$/,
                  pval = (pwd) => {
                      let ok = true,
                          pats = [/[A-Z]+/, /[0-9]+/,
                                  /[_\-\!\?\/\\@#$%\^&\*\(\)\+\|\]\[\{\}]+/];
                      if (pwd.length < 8) {
                          ok = false;
                      };
                      pats.map(p => { ok = (pwd.search(p) !== -1)});
                      return ok;
                  };
              if (!username_val) {
                  showErr(username, "username missing!");
                  return false;
              } else if (!/[A-Za-z0-9_]+/.test(username_val)) {
                  showErr(username, "letters, numbers and '_' only");
                  return false;
              } else {
                  console.log(`username: ${username_val}`);
                  out.username = username_val;
              };
              if (!pw1_val) {
                  showErr(pw1, "password missing!");
                  return false;
              } else if (!pw2_val) {
                  showErr(pw2, "please repeat password");
                  return false;
              } else if (!pval(pw1_val)) {
                  showErr(pw1, ('password must be at least 8 characters' +
                                ' long and contain at least 1 number, at least 1 ' +
                                'capital letter, and at least 1 special character'));
                  return false;
              } else if (!(pw1_val === pw2_val)) {
                  showErr(pw2, "passwords must match!");
                  return false;
              } else {
                  console.log(`pw: ${pw1_val}`);
                  out.password = pw1_val;
              };
              if (!email_val) {
                  showErr(email, "email missing!");
                  return false;
              } else if (!email_val.match(email_pat)) {
                  showErr(email, 'invalid email address!');
                  return false;
              } else {
                  console.log(`email: ${email_val}`);
                  out.email = email_val;
              };
              out['public'] = pub_val;
              retriever.POST('users', out)
                  .then(js => {
                      username = js.name;
                      user_id = js.id;
                      let l = retriever.POST('login',
                                            {username, password: pw1_val})
                      console.log(`POST login: ${l}`);
                      return l;
                  })
                  .then(js => retriever.user = js['results'][0])
                  .catch(err => showErr(target, err))
          },
          showFavs = () => {
            bigTarget.empty();
            retriever.GET('likes', retriever.userId)
                .then(js => tabler.makeTable(js.model, js.result))
                .catch(err => bigTarget.append(`<p class="bg-danger">${err}</p>`));
          },
          showProfile = () => {
              let closeCB = () => $("#profileWidget").remove(),
                  user;
              bigTarget.empty();
              retriever.GET('users', retriever.userId)
                  .on(js => {
                      user = js.result[0],
                      profile = $('<div class="col-md-8" id="userProfile"><p>' +
                                  `<strong>Username: </strong> ${user.name}</p>` +
                                  `<p><strong>Email: </strong> ${user.email}</p>` +
                                  `<p><strong>Public: </strong> ${user.public ? 'Yes' : 'No'}` +
                                  '<p><button type="button" id="profile-likes">' +
                                  'Show likes</button>&nbsp;<button type="button" ' +
                                  'class="btn btn-danger btn-xs x" aria-label="Close">' +
                                  '<span aria-hidden="true">&times;</span></button>' +
                                  '</p></div>');
                      bigTarget.append(profile);
                      profile.on('click', '#profile-likes', showFavs);
                      profile.on('click', '.x',
                                 e => $(e.target).parents('#userProfile').remove());
                  });
          },
          showUser = () => {
              let loggedIn = getLoggedInWidget();
              target.append(loggedIn);
              loggedIn.on('click', '#profile', showProfile);
              loggedIn.on('click', '#likes', showFavs);
              loggedIn.on('click', '#logout', () => (retriever.clearCreds(), init()));
          },
          logIn = e => {
              let tgt = $(e.target).parents('form'),
                  username = target.find('#username').val(),
                  password = target.find('#password').val();
              $("#err").remove();
              retriever.POST('login', {username, password})
                  .then(js => {
                          console.log(js);
                          retriever.user = js.result[0];
                          init();
                  })
                  .catch(err => {
                      console.log(err); 
                      $(`<p class="bg-danger err">${err}</p>`).appendTo(tgt);
                  })
          },
          showLogin = () => {
              target.append(logInWidget);
              logInWidget.on('click', '#log-in', logIn);
              logInWidget.on('click', '#sign-up', () => {
                  bigTarget.append(signUpWidget);
                  $("#go").on('click', signUp);
              });
          };
        init = () => {
            console.log('UserWidget init');
            target.empty();
            if (!!retriever.user) {
                console.log(`username: ${retriever.user.username}`);
                showUser();
            } else {
                console.log('not logged in');
                showLogin();
            };
        };
    init();
}
