<?php
/* Plugin Name: Benchmark Fixture */
add_action('admin_init', function () { register_setting('bench_group', 'bench_label', ['type'=>'string', 'default'=>'', 'sanitize_callback'=>'sanitize_text_field']); });
