import app
from routes.index import user_detail
# from routes.index import profile
import cProfile
from pstats import Stats

# bash
# apt install apache2-utils
# ab -n 100 -c 10 -C 'session=388a0388-c757-4972-bdd1-2cefac313180' http://localhost/user/setting  # 10条请求，并发数2

# sudo apt-get -y install graphviz
# sudo pip3 install gprof2dot
# python3 test_profile.py
# gprof2dot -f pstats test_profile.pstat | dot -Tpng -o output.png


def profile_request(path, cookie, f):
    a = app.configured_app()
    pr = cProfile.Profile()
    headers = {'Cookie': cookie}

    with a.test_request_context(path, headers=headers):
        pr.enable()

        # r = f()
        # assert type(r) == str, r
        f('user1')

        pr.disable()

    # pr.dump_stats('test_profile.out')
    # pr.create_stats()
    # s = Stats(pr)
    pr.create_stats()
    s = Stats(pr).sort_stats('cumulative')
    s.dump_stats('test_profile.pstat')

    s.print_stats('.*plbbs.*')
    # s.print_callers()


if __name__ == '__main__':
    # path = '/profile'
    path = '/user/user1'
    cookie = 'session=95375960-c278-4abf-8efe-dd5b3f2eca39'
    # profile_request(path, cookie, profile)
    profile_request(path, cookie, user_detail)
