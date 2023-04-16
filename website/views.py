# create blueprint for all the route
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db


# ML import
import pickle
import nltk
from nltk.corpus import stopwords
import re 
from nltk.stem.porter import PorterStemmer
from keras.preprocessing.text import Tokenizer
# from keras.utils import pad_sequences
from keras.utils.data_utils import pad_sequences


# from tensorflow.keras.preprocessing.sequence import pad_sequences
import string 
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

ps = PorterStemmer()
tokenizer = Tokenizer(num_words=20000)

model = pickle.load(open('model2_221.pkl', 'rb'))


views = Blueprint("views",__name__)

# ML model
def predict(text):
    
    print(text)
    tokenizer.fit_on_texts([text])


    new_sequence = tokenizer.texts_to_sequences([text])
    print(new_sequence)

    new_data = pad_sequences(new_sequence, maxlen=100)
    print(new_data)

    prediction = model.predict(new_data)
    score = prediction[0][0]
    
    # print(type(score))
    
    # score = round(score,2) * 100
    import math

    
    def round_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n * multiplier) / multiplier
    
    if score < 0.5:
        score = 1 - score
    
    
    # score = str(score)

    prediction_label = np.round(prediction[0][0])
    print(prediction_label)
    print("truthful" if prediction_label==1 else "deceptive")
    truthful_str = "truthful" +" " +"("+str(round_up(score*100,2)) + "%" +")"
    deceptive_str = "deceptive" +" " +"("+str(round_up(score*100,2))+"%"+")"
    # return "truthful" +" " +"("+str(prediction[0][0]) +")" if prediction_label==1 else "deceptive" +" " +"("+str(prediction[0][0])+")"
    return truthful_str if prediction_label==1 else deceptive_str







# either route will lead to the same page
@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/create-post", methods=['GET','POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')
        text_link = request.form.get('text_link')
        
        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, text_link=text_link, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!!!', category='success')   
            return redirect(url_for('views.home')) 
            
            
    return render_template('createpost.html', user= current_user)

@views.route('/delete-post/<id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    
    if not post:
        flash("Post does not exist.",category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')
    
    return redirect(url_for('views.home'))


@views.route('/posts/<username>')
@login_required
def post(username):
    user = User.query.filter_by(username=username).first()
    
    
    if not user:
        flash('No user with that username exists', category='error')
        return redirect(url_for('views.home'))
    
    # posts = Post.query.filter_by(author=user.id).all()
    posts = user.posts
    
    return render_template('posts.html',user=current_user,posts=posts, username=username)





@views.route('/create-comment/<post_id>',methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    # print(text+"(category)")
    # print(type(text))
    
    prediction = predict(text)
    print(prediction)
    
    # text = text + " " + "(" +prediction + ")"

    
    if not text:
        flash('Comment can not apply', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text,label=prediction,author=current_user.id,post_id=post_id)
            # print(comment)
            # print(type(comment))
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    
    return redirect(url_for('views.home'))






@views.route('/delete-comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not comment:
        flash("Comment does not exist.",category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Post deleted', category='success')
    
    return redirect(url_for('views.home'))


