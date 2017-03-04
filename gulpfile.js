/**
 * Created by kmartineaumcfarlane on 27/08/2015.
 */
// Utility function to do string formatting
String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

// Replace this with the name of your application
var APP_NAME = 'usercontent';
var REQUIRES_THIRD_PARTY_CSS = false;
var webpack = require('webpack-stream');


// Load all the plugins you have installed
// ====================================================== //

var gulp = require('gulp'),
    sass = require('gulp-sass'),
    autoprefixer = require('gulp-autoprefixer'),
    minifycss = require('gulp-minify-css'),
    rename = require('gulp-rename'),
    del = require('del'),
    wrap = require('gulp-wrap'),
    scsslint = require('gulp-scss-lint'),
    gutil = require('gulp-util'),
    concat = require('gulp-concat'),
    merge = require('merge-stream'),
    uglify = require('gulp-uglify'),
    jshint = require('gulp-jshint'),
    stylish = require('jshint-stylish'),
    rebase = require('gulp-css-rebase-urls');

// Error handling
// ====================================================== //

var onError = function (err) {
    console.log(err);
};

// Defining paths

var js_settings = [
  './static/usercontent/js/user_status_activate.js',
  './static/usercontent/js/usercontent_form.js'
];

// source and destination paths
var paths = {
    sass: {
        src: './src/sass/**/*.scss',
        dest: './static/{0}/css/'.f(APP_NAME)
    },

    js: {
        src: js_settings,
        dest: './static/{0}/built/js/'.f(APP_NAME)
    },

    css: {
        src: './static/{0}/css/**/*.css'.f(APP_NAME),
        dest: './static/{0}/built/css'.f(APP_NAME)
    },

    // JSHint Javascript (only code written by us, excludes libraries)
    jshint: {
        src: './static/js/**/*.js'
    }

};

// SASS compilation and auto-prefixing
// ====================================================== //


// Linting SASS
// ====================================================== //
// lint according to the config set in scss-lint.yml, then write issues to a file scssLintReport.xml
// and summarise issues in the terminal

gulp.task('sass', function(){
    var pipe = gulp.src(paths.sass.src)

        // compile sass, sending any errors to the terminal and keeping gulp running when it does error
        .pipe(sass({
            errLogToConsole: true
        }))

        // auto-prefix the file in the stream
        .pipe(autoprefixer('last 2 version', 'ie 9', 'ios 6', 'android 4'));

    if(REQUIRES_THIRD_PARTY_CSS){
        // write the file in the stream to the destination directory
        pipe.pipe(gulp.dest(paths.sass.dest))
    }else{
        pipe.pipe(rebase({root: paths.css.dest}))
        .pipe(gulp.dest(paths.css.dest))
        .pipe(rename({suffix: '.min'}))
        .pipe(minifycss())
        .pipe(gulp.dest(paths.css.dest))
    }


});

var myCustomReporter = function(file) {
  if (!file.scsslint.success) {
    gutil.log(gutil.colors.cyan('scss-lint: ')+file.scsslint.issues.length + ' issues found in ' + file.path);
  }
};

gulp.task('scss-lint', function() {
  gulp.src(paths.sass.src)
    .pipe(scsslint({
        'config': 'scss-lint.yml',
        'reporterOutput': 'scssLintReport.xml',
        customReport: myCustomReporter
    }));
});


// Removing previously built files
// ====================================================== //
gulp.task('clean_css', function(cb) {
    del(['./static/{0}/built/css/*.css'.f(APP_NAME)], cb);
});

gulp.task('clean_js', function(cb) {
    del(['./static/{0}/built/js/*.js'.f(APP_NAME)], cb);
});

gulp.task('clean', ['clean_css', 'clean_js']);


// CSS - concatenate and mini-fy
// ====================================================== //
gulp.task('css', ['clean_css'], function() {
    gulp.src(paths.css.src)
        .pipe(rebase({root: paths.css.dest}))
        .pipe(gulp.dest(paths.css.dest))
        .pipe(rename({suffix: '.min'}))
        .pipe(minifycss())
        .pipe(gulp.dest(paths.css.dest))
});

// JS - concatenate and mini-fy
// ====================================================== //
gulp.task('js', ['clean_js'], function() {
    gulp.src(paths.js.src)
        .pipe(concat('usercontent.js'))
        .pipe(gulp.dest(paths.js.dest))
        .pipe(rename({suffix: '.min'}))
        .pipe(uglify())
        .pipe(gulp.dest(paths.js.dest))

});

// JS - lint
// ====================================================== //
gulp.task('js-lint', function() {
    return gulp.src(paths.jshint.src)
        .pipe(jshint())
        .pipe(jshint.reporter(stylish));
});

// WATCH
// ====================================================== //
// run gulp watch to call the default task and then start to watch
gulp.task('watch', ['default'], function() {
    gulp.watch(paths.sass.src, ['sass']);
    gulp.watch(paths.js.src , ['js']);
    gulp.watch(paths.css.src , ['css']);
});







gulp.task('react-prod', function(){

    return gulp.src('./src/js/index.js')
    .pipe(webpack( require('./webpack.config.production.js') ))
    .pipe(gulp.dest('./static/usercontent/js/built'));

});

gulp.task('react-dev', function(){

    return gulp.src('./src/js/index.js')
    .pipe(webpack( require('./webpack.config.js') ))
    .pipe(gulp.dest('./static/usercontent/js/built'));

});


gulp.task('watch-react', function() {
    gulp.watch('./src/js/**/*.js', ['react-dev']);
});



// DEFAULT
// ====================================================== //
// Make the default task (run by typing gulp) execute the tasks in the array -
// don't make the default task the watch because Jenkins will then start to gulp
// watch when it executes gulp...and never finish
gulp.task('default', ['sass', 'css', 'js', 'react-prod']);



