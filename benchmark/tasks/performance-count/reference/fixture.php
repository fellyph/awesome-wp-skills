<?php
/* Plugin Name: Benchmark Fixture */
function bench_published_count(){return (int)wp_count_posts('post')->publish;}
