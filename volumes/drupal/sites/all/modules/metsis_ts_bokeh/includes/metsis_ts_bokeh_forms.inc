<?php
/**
 * @param $form
 * @param $form_state
 *
 * @return mixed
 */

function metsis_ts_bokeh_init_form($form, &$form_state) {
  global $base_url;
  $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_data_uri'] = NULL;
  $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_plot_query'] = NULL;
  $form['data_uri'] = [
    '#type' => 'textfield',
    '#title' => t("Enter service URL:"),
    '#required' => TRUE,
  ];
  $form['actions'] = [
    '#type' => 'actions',
  ];
  $form['actions']['submit'] = [
    '#type' => 'submit',
    '#value' => t('Submit'),
    '#submit' => ['metsis_ts_bokeh_init_submit'],
  ];
  return $form;
}

/**
 * @param $form
 * @param $form_state
 */
function metsis_ts_bokeh_init_submit($form, &$form_state) {
  /**
   * dummy function.
   * sends user input to metsis_ts_bokeh_plot_form()
   * TO BE REMOVED when this module is connected to the other METSIS modules in
   * production env.
   */
  //lists_session('metsis_ts_bokeh_data_uri', $form_state['values']['data_uri']);
  $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_data_uri'] = $form_state['values']['data_uri'];
  drupal_goto(TS_BOKEH_PLOT_NODE);
}

/**
 * @param $form
 * @param $form_state
 *
 * @return mixed
 */
function metsis_ts_bokeh_plot_form($form, &$form_state) {

  /**
   * build form based on JSON object returned by pybasket
   */
  $default_x_axis = "no default set";
  $form['x_axis'] = [
    '#type' => 'select',
    '#options' => ['time' => 'time'],
    '#default_value' => $default_x_axis,
    '#description' => t(''),
    '#empty' => t(''),
  ];
  $default_y_axis = "no default set";

  $form['y_axis'] = [
    '#type' => 'select',
    '#options' => adc_get_ts_bokeh_plot_y_vars(),
    '#default_value' => $default_y_axis,
    '#description' => t(''),
    '#empty' => t(''),
  ];
  $form['actions'] = [
    '#type' => 'actions',
  ];
  $form['actions']['submit'] = [
    '#type' => 'submit',
    '#value' => t('Submit'),
    '#submit' => ['metsis_ts_bokeh_plot_submit'],
  ];

  if (isset($form_state['storage']['results'])) {
    $form['results'] = ['#value' => $form_state['storage']['results'],];
  }
  return $form;
}

/**
 * @param $form
 * @param $form_state
 */
function metsis_ts_bokeh_plot_submit($form, &$form_state) {
  $_SESSION['metsis_ts_bokeh'][session_id()]['metsis_ts_bokeh_plot_query'] = adc_get_ts_bokeh_plot_query($form_state);
}
