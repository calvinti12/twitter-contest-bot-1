
var gulp = require('gulp'),
    webpack = require('webpack-stream');


gulp.task('react-prod', function(){

    return gulp.src('./src/js/app.jsx')
    .pipe(webpack( require('./webpack.config.production.js') ))
    .pipe(gulp.dest('./static/js/built'));

});

gulp.task('react-dev', function(){

    return gulp.src('./src/js/app.jsx')
    .pipe(webpack( require('./webpack.config.js') ))
    .pipe(gulp.dest('./static/js/built'));

});




gulp.task('watch', function() {
    gulp.watch('./src/js/**/*.jsx', ['react-dev']);
});






gulp.task('default', ['react-prod']);



