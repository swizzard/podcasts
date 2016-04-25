const gulp = require('gulp');
const browserify = require('browserify');
const babelify = require('babelify')
const eslint = require('gulp-eslint');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const uglify = require('gulp-uglify');
const sourcemaps = require('gulp-sourcemaps');
const livereload = require('gulp-livereload');

gulp.task('build', () => {
    return browserify({entries: './src/js/es6/app.js',
                       debug: true})
        .transform('babelify', {presets: ['es2015']})
        .bundle()
        .pipe(source('app.js'))
        .pipe(buffer())
        // .pipe(uglify())
        .pipe(sourcemaps.write('./maps'))
        .pipe(gulp.dest('./src/js/dist'))
        .pipe(livereload());
});

gulp.task('lint', () => {
    return gulp.src('./src/js/es6/app.js')
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failOnError())
})

gulp.task('watch', () => {
    gulp.watch('./src/js/es6/*.js', ['lint', 'build']);
    })

gulp.task('default', ['build', 'watch']);
