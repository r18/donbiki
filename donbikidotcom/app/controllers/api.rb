Donbikidotcom::App.controllers :api do

  post "/post_dtweet", :csrf_protection => false do
    @dtweet = Dtweet.new(params.require(:dtweet).permit(:user, :body, :text, :tweetId))
    if @dtweet.save
      puts "Success"
    else 
      puts "Error to save"
    end 
  end 
  # get :index, :map => '/foo/bar' do
  #   session[:foo] = 'bar'
  #   render 'index'
  # end

  # get :sample, :map => '/sample/url', :provides => [:any, :js] do
  #   case content_type
  #     when :js then ...
  #     else ...
  # end

  # get :foo, :with => :id do
  #   'Maps to url '/foo/#{params[:id]}''
  # end

  # get '/example' do
  #   'Hello world!'
  # end
end
