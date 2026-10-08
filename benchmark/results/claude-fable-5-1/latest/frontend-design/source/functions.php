<?php
/**
 * Northline theme setup.
 */

add_action( 'after_setup_theme', function () {
	add_theme_support( 'editor-styles' );
	add_editor_style( 'style.css' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'post-thumbnails' );
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'northline', get_stylesheet_uri(), array(), '1.0.0' );
} );

add_action( 'init', function () {
	register_block_pattern_category(
		'northline',
		array( 'label' => __( 'Northline', 'benchmark-fixture' ) )
	);
} );
