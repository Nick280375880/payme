# -*- coding: utf-8 -*-
"""
The basic view logic here.

For example: signin, signup, homepage , etc.
"""

import logging
import functools

from django.views import generic

from portal import forms
from portal import models
from portal.views import utils

LOG = logging.getLogger(__name__)


def check_authentication(func):
    """The decorator will check username existed in session. If it is continue.
    """
    @functools.wraps(func)
    def _check_authentication(req, **kwargs):
        username = req.session.get('username')
        if not username:
            return signin(req)
        else:
            return func(req)

    return _check_authentication


class SignIn(generic.FormView):

    form_class = forms.SignInForm
    template_name = 'portal/sign_in.html'

    def form_valid(self, form):
        data = form.cleaned_data
        users = models.User.objects.filter(username=data['username'])
        if users and users[0].password == data['password']:
            LOG.debug('%s login success.' % users)
            utils.set_session(self.request, users[0].username)
            return portal(self.request)
        else:
            LOG.debug("%s login failed." % users)
            return utils.render('sign_in.html',
                                {'errors': 'Username or password is wrong',
                                 'form': form})

signin = SignIn.as_view()


class SignUp(generic.FormView):

    template_name = 'portal/sign_up.html'
    form_class = forms.SignUpForm

    def form_valid(self, form):
        data = form.cleaned_data
        user = models.User(**data)
        user.save()
        return utils.render('portal.html', {})

signup = SignUp.as_view()


def portal(req):
    user = utils.get_user_obj(req)
    houses = user.house_set.all()
    orders = user.order_set.all()
    return utils.render('portal.html', {'houses': houses,
                                        'orders': orders})


class ChargeRent(generic.FormView):
    form_class = forms.ChargeRentForm
    template_name = 'portal/charge_rent.html'

    def form_valid(self, form):
        data = form.cleaned_data
        me = utils.get_user_obj(self.request)
        house = models.House(owner=me,
                             house_name=data['location_area'],
                             house_size=int(data['house_size']))
        house.save()
        return portal(self.request)

chargerent = check_authentication(ChargeRent.as_view())


@check_authentication
def payrent(req):
    pass
