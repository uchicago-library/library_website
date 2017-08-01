"use strict";

var gulp = require('gulp');
var sass = require('gulp-sass'); // Requires the gulp-sass plugin


gulp.task('sass', function(){
  return gulp.src('base/static/base/css/loop-styles.scss')
    .pipe(sass()) // Using gulp-sass
    .pipe(gulp.dest('base/static/base/css'))
});


gulp.task("default", ["sass"], function() {
});