class CreateDtweets < ActiveRecord::Migration
  def self.up
    create_table :dtweets do |t|
      t.string :user
      t.string :body
      t.timestamps
    end
  end

  def self.down
    drop_table :dtweets
  end
end
