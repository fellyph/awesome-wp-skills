<?php
/**
 * Northline Benchmark block theme.
 *
 * @package benchmark-fixture
 */

if ( ! function_exists( 'northline_setup' ) ) {
	/**
	 * Theme supports.
	 */
	function northline_setup() {
		add_theme_support( 'editor-styles' );
		add_editor_style( 'style.css' );
		add_theme_support( 'post-thumbnails' );
		add_theme_support( 'responsive-embeds' );
		add_theme_support( 'wp-block-styles' );
	}
}
add_action( 'after_setup_theme', 'northline_setup' );

if ( ! function_exists( 'northline_enqueue_styles' ) ) {
	/**
	 * Frontend stylesheet.
	 */
	function northline_enqueue_styles() {
		wp_enqueue_style(
			'northline-style',
			get_stylesheet_uri(),
			array(),
			wp_get_theme()->get( 'Version' )
		);
	}
}
add_action( 'wp_enqueue_scripts', 'northline_enqueue_styles' );

if ( ! function_exists( 'northline_pattern_categories' ) ) {
	/**
	 * Register a pattern category for theme patterns.
	 */
	function northline_pattern_categories() {
		register_block_pattern_category(
			'northline',
			array(
				'label'       => __( 'Northline', 'benchmark-fixture' ),
				'description' => __( 'Landing page sections for the Northline agency theme.', 'benchmark-fixture' ),
			)
		);
	}
}
add_action( 'init', 'northline_pattern_categories' );
