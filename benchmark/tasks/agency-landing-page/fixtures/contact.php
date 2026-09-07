<?php
/** Fixed synthetic contact fixture. No mail or external delivery. */
add_filter('show_admin_bar', '__return_false');
add_shortcode('benchmark_contact', function () {
    $status = isset($_GET['contact']) && $_GET['contact'] === 'sent' ? '<p role="status">Thanks. Your project enquiry is saved.</p>' : '';
    return $status . '<form class="bench-contact" method="post" action="' . esc_url(admin_url('admin-post.php')) . '">' .
        '<input type="hidden" name="action" value="benchmark_contact">' . wp_nonce_field('benchmark_contact', 'benchmark_nonce', true, false) .
        '<label>Name<input name="client_name" autocomplete="name" required maxlength="120"></label>' .
        '<label>Email<input type="email" name="email" autocomplete="email" required maxlength="200"></label>' .
        '<label>Message<textarea name="message" required maxlength="2000"></textarea></label>' .
        '<button type="submit">Send enquiry</button></form>';
});
function benchmark_contact_submit() {
    if (!isset($_POST['benchmark_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['benchmark_nonce'])), 'benchmark_contact')) {
        wp_die('Invalid request', 'Invalid request', array('response' => 403));
    }
    $name = sanitize_text_field(wp_unslash($_POST['client_name'] ?? ''));
    $email = sanitize_email(wp_unslash($_POST['email'] ?? ''));
    $message = sanitize_textarea_field(wp_unslash($_POST['message'] ?? ''));
    if (!$name || !is_email($email) || !$message || strlen($name) > 120 || strlen($message) > 2000) {
        wp_die('Please complete all fields with a valid email.', 'Invalid submission', array('response' => 400));
    }
    $items = get_option('benchmark_submissions', array());
    $items[] = array('name' => $name, 'email' => $email, 'message' => $message);
    update_option('benchmark_submissions', array_slice($items, -20), false);
    wp_safe_redirect(home_url('/?contact=sent#contact'));
    exit;
}
add_action('admin_post_benchmark_contact', 'benchmark_contact_submit');
add_action('admin_post_nopriv_benchmark_contact', 'benchmark_contact_submit');
