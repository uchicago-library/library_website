'use strict';
 
var gulp = require('gulp');
var sass = require('gulp-sass');
 
gulp.task('sass', function () {
  return gulp.src('base/static/base/css/loop/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('base/static/base/css/'));
});
 
gulp.task('sass:watch', function () {
  gulp.watch('base/static/base/css/loop/*.scss', ['sass']);
});

gulp.task("default", ["sass"], function() {
});

var gulp = require('gulp');
var sass = require('gulp-sass'); // Requires the gulp-sass plugin


gulp.task('sass', function(){
  return gulp.src('base/static/base/css/loop/*.scss') // Gets all files ending with .scss in src/scss and children dirs
    .pipe(sass()) // Using gulp-sass
    .pipe(gulp.dest('base/static/base/css'))
});

gulp.task('watch', ['sass'], function(){
  gulp.watch('base/static/base/css/loop/*.scss', ['sass']);
})

gulp.task("default", ["sass", "watch"], function() {
});
