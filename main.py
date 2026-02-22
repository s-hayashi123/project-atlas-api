import os
from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from typing import Optional, List

# --- Database setup ---

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/atlas"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)  # BUG: UNIQUE制約なし (P02-01)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False
    )  # BUG: ON DELETE なし (P02-08)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # BUG: ON DELETE なし (P02-08)
    role = Column(String, nullable=False, default="member")
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="members")


# --- Pydantic Schemas ---
# BUG: description / example が未整備 (P01-05)
# BUG: extra="forbid" 未設定 (P02-07)


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str
    email: str


class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TeamMemberCreate(BaseModel):
    user_id: int
    role: Optional[str] = "member"


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: str
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- App ---
# BUG: グローバル例外ハンドラなし (P02-04)

app = FastAPI(title="Project Atlas API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Health ---


@app.get("/health")
def health_check():
    # BUG: DB確認なし (P01-07)
    return {"status": "ok"}


# --- Users CRUD ---


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # BUG: name が空文字でも通る (P01-08)
    # BUG: email の重複チェックなし (P02-01)
    print(f"Creating user: {user.name}")  # BUG: print()でログ出力 (P01-09)
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"User created with id: {db_user.id}")  # BUG: print()でログ出力 (P01-09)
    return db_user


@app.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    print("Fetching all users")  # BUG: print()でログ出力 (P01-09)
    users = db.query(User).all()
    # BUG: DB空だと500 (P01-03)
    # first() の結果を参照しようとしてエラーになるパターン
    first_user = users[0]
    print(f"First user: {first_user.name}")
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    print(f"Fetching user: {user_id}")  # BUG: print()でログ出力 (P01-09)
    user = db.query(User).filter(User.id == user_id).first()
    # BUG: 存在しない場合 None を返して属性参照で500 (P02-02)
    print(f"Found user: {user.name}")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    print(f"Updating user: {user_id}")  # BUG: print()でログ出力 (P01-09)
    user = db.query(User).filter(User.id == user_id).first()
    # BUG: 存在チェックなし
    # BUG: 既存メールへの変更チェックなし (P02-03)
    user.name = user_data.name
    user.email = user_data.email
    db.commit()
    db.refresh(user)
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, user_data: UserPatch, db: Session = Depends(get_db)):
    print(f"Patching user: {user_id}")  # BUG: print()でログ出力 (P01-09)
    user = db.query(User).filter(User.id == user_id).first()
    # BUG: 部分更新が壊れる - 未送信フィールドがnullになる (P02-05)
    user.name = user_data.name
    user.email = user_data.email
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    print(f"Deleting user: {user_id}")  # BUG: print()でログ出力 (P01-09)
    user = db.query(User).filter(User.id == user_id).first()
    # BUG: 外部キー依存の考慮なし (P02-08)
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


# --- Teams CRUD ---


@app.post("/teams", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    print(f"Creating team: {team.name}")  # BUG: print()でログ出力 (P01-09)
    db_team = Team(name=team.name, description=team.description)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@app.get("/teams", response_model=List[TeamResponse])
def list_teams(db: Session = Depends(get_db)):
    print("Fetching all teams")
    teams = db.query(Team).all()
    return teams


@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    print(f"Fetching team: {team_id}")
    team = db.query(Team).filter(Team.id == team_id).first()
    return team


# --- Team Members ---


@app.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
def add_team_member(
    team_id: int, member: TeamMemberCreate, db: Session = Depends(get_db)
):
    print(f"Adding member to team {team_id}")
    db_member = TeamMember(team_id=team_id, user_id=member.user_id, role=member.role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@app.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
def list_team_members(team_id: int, db: Session = Depends(get_db)):
    print(f"Fetching members for team {team_id}")
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return members
