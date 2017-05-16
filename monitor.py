from flask import make_response
from flask import redirect
from flask import render_template
from flask import request

import ad
from app import app


@app.route('/ads/', methods=['GET', 'POST'])
def ad_list():
    if request.method == 'GET':
        # List all ads.
        context = {'ads': ad.get_ads()}
        return render_template('ad_list.html', **context)
    elif request.method == 'POST':
        # Create an ad.
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


@app.route('/ads/<int:ad_id>', methods=['GET', 'POST', 'DELETE'])
def ad_detail(ad_id):
    if request.method == 'GET':
        # Get an ad.
        context = {'ad': ad.get_ad_by_id(ad_id)}
        return render_template('ad_detail.html', **context)
    elif request.method == 'POST':
        # Update an ad.
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
    elif request.method == 'DELETE':
        # Delete an ad.
        ad.remove_ad(ad_id)
        return make_response(redirect('/ads/'))