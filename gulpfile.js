const gulp = require('gulp');
const browserify = require('browserify');
const babelify = require('babelify')
const eslint = require('gulp-eslint');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const uglify = require('gulp-uglify');
const sourcemaps = require('gulp-sourcemaps');
const livereload = require('gulp-livereload');
const cleanCSS = require('gulp-clean-css');
const csslint = require('gulp-csslint');
const concatCss = require('gulp-concat-css');

gulp.task('build', () => {
     return browserify({entries: ['src/js/retriever.js',
                                  'src/js/tabler.js',
                                  'src/js/searcher.js',
                                  'src/js/user.js',
                                  'src/js/app.js'],
                       debug: true,
                       sourceType: 'module'})
        .transform('babelify', {presets: ['es2015']})
        .bundle()
        .pipe(source('app.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(sourcemaps.write('./src/js/maps'))
        .pipe(gulp.dest('./dist/js'))
        .pipe(livereload());
});

gulp.task('lint', () => {
    return gulp.src('./src/js/*.js')
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failOnError());
});

gulp.task('css-build', () => {
    return gulp.src(['./src/css/main.css'])
        .pipe(sourcemaps.init())
        .pipe(cleanCSS())
        .pipe(concatCss('bundle.css'))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('./dist/css'));
});

gulp.task('css-lint', () => {
    return gulp.src('./src/css/*.css')
        .pipe(csslint({ids: false}))
        .pipe(csslint.reporter())
        .pipe(csslint.reporter('fail'));
});

gulp.task('watch', () => {
    gulp.watch('src/js/*.js', ['lint', 'build']);
    gulp.watch('src/css/*.css', ['css-lint', 'css-build']);
});

gulp.task('default', ['build', 'watch']);

