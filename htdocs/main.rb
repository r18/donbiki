require 'sinatra'
require 'sinatra/reloader'
require 'active_record'
require 'uri'
require 'logger'
require 'sass'

ActiveRecord::Base.establish_connection(
  "adapter" => "sqlite3",
  "database" => "./tweets.db"
)

class Donbikitweets < ActiveRecord::Base
end

#set :public_folder, File.dirname(__FILE__) + '/static'
configure do
end
helpers do
end
get '/' do
  @donbikis = Donbikitweets.order("id desc").all
  erb :index
end

get '/about' do
        erb :about
end

get '/about' do
        "hogehoge"
end

post '/new' do
  Comment.create({:body => params[:body]})
  redirect '/'
end
post '/delete' do
  Comment.find(params[:id]).destroy();
  redirect '/'
end

get '/bootstrap.css' do
        scss :bootstrap
end
get '/js/bootstrap.min.js' do
end
