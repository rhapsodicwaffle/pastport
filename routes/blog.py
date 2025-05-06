from flask import Blueprint, render_template, request, redirect, url_for, abort, session
from models import db, BlogPost, Bookmark

blog = Blueprint('blog', __name__, template_folder='../templates')


@blog.route('/blog')
def view_blog():
    posts = BlogPost.query.order_by(BlogPost.date.desc()).all()

    bookmarked_blog_ids = set()
    if 'user' in session:
        bookmarks = Bookmark.query.filter_by(user_id=session['user'], item_type='blog').all()
        bookmarked_blog_ids = set(b.item_id for b in bookmarks)

    return render_template('blog.html', posts=posts, bookmarked_blog_ids=bookmarked_blog_ids)


@blog.route('/blog/new', methods=['GET', 'POST'])
def new_blog():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = BlogPost(title=title, content=content, author=session['user'])
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog.view_blog'))
    return render_template('new_blog.html')

@blog.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_blog(post_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    post = BlogPost.query.get_or_404(post_id)
    if post.author != session['user']:
        abort(403)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('blog.view_blog'))

    return render_template('edit_blog.html', post=post)

@blog.route('/blog/delete/<int:post_id>')
def delete_blog(post_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    post = BlogPost.query.get_or_404(post_id)
    if post.author != session['user']:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.view_blog'))

