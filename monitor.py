from flask import make_response
from flask import redirect
from flask import render_template
from flask import request

import ad
from app import app


@app.route('/ads/', methods=['GET'])
def list_ad():
    context = {
        'ads': sorted(ad.get_ads(), key=lambda a: a.id),
        'auto_refresh': request.args.get('auto_refresh', 0)
    }
    return render_template('ad_list.html', **context)


@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    context = {'ad': ad.get_ad(ad_id)}
    return render_template('ad_detail.html', **context)


@app.route('/ads/add', methods=['POST'])
def add_ad():
    ad.create_ad(**request.form.to_dict())
    return make_response(redirect('/ads'))


@app.route('/ads/<int:ad_id>/update', methods=['POST'])
def update_ad(ad_id):
    ad.update_ad(ad_id, **request.form.to_dict())
    return make_response(redirect('/ads/'))


@app.route('/ads/<int:ad_id>/delete', methods=['POST'])
def delete_ad(ad_id):
    ad.delete_ad(ad_id)
    return make_response(redirect('/ads/'))
