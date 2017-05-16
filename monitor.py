from flask import make_response
from flask import redirect
from flask import render_template
from flask import request

import ad
from app import app


@app.route('/ads/', methods=['GET'])
def list_ad():
    context = {'ads': ad.get_ads()}
    return render_template('ad_list.html', **context)


@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    context = {'ad': ad.get_ad(ad_id)}
    return render_template('ad_detail.html', **context)


@app.route('/ads/add', methods=['POST'])
def add_ad():
    ad.create_or_update_ad(
        ad_id=None,
        dest_url=request.form['dest_url'],
        image_src=request.form['image_src'],
        width=request.form['width'],
        height=request.form['height'],
        cpm=float(request.form['cpm']),
        daily_budget=float(request.form['daily_budget']),
    )
    return make_response(redirect('/ads'))


@app.route('/ads/<int:ad_id>/update', methods=['POST'])
def update_ad(ad_id):
    ad.create_or_update_ad(
        ad_id=ad_id,
        dest_url=request.form['dest_url'],
        image_src=request.form['image_src'],
        width=request.form['width'],
        height=request.form['height'],
        cpm=float(request.form['cpm']),
        daily_budget=float(request.form['daily_budget']),
    )
    return make_response(redirect('/ads/'))


@app.route('/ads/<int:ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    ad.delete_ad(ad_id)
    return make_response(redirect('/ads/'))